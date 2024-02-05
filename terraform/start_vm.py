import logging
import uuid
import time
import os
import sys
from multiprocessing import Process
from threading import Thread, Lock
from datetime import timedelta
import urllib.request
import tempfile
import socket
import json

from django.db import transaction
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from django.core.files import File
from django.conf import settings

from vmauto.models import VirtualMachine, GraphicsProcessingUnit, Server
from vmauto.automation.AutomationException import AutomationStepFailedException
from experience.models import StreamArgsPreset
from vmauto.automation.automation import choose_automation
from django_slack_notifications.utils import send_text

from pexpect import pxssh, TIMEOUT


logger = logging.getLogger(__name__)


def wait_port_is_open(host, port, timeout_seconds=600):
    start_time_seconds = time.time()
    while time.time() - start_time_seconds < timeout_seconds:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except socket.gaierror as e:
            logger.exception(e)
        time.sleep(5)
    return False


def get_vma_host_name():
    host_name = socket.gethostname()
    return host_name


def get_diagnostic(vm):
    ge_port_is_open = wait_port_is_open(vm.ip, 47989)
    test_screenshot_data = None
    if ge_port_is_open:
        sap = StreamArgsPreset.objects.get(use_for_test=True)
        query_string = urllib.parse.urlencode({
            'streamArgsFormat': sap.native_stream_args
        })
        try:
            with urllib.request.urlopen('http://' + vm.ip + ':47989/test?' + query_string, b'', 30) as f:
                test_screenshot_data = f.read()
        except Exception as e:
            logger.exception(e)

    diag_output = None
    if ge_port_is_open:
        try:
            with urllib.request.urlopen('http://' + vm.ip + ':47989/diag', b'', 30) as f:
                diag_output = f.read().decode('utf-8')
        except Exception as e:
            logger.exception(e)
    return ge_port_is_open, diag_output, test_screenshot_data


class State(object):
    def __init__(self):
        self.lock = Lock()
        self.servers_in_progress = set()
        self.vms_in_progress = set()


class VMAThread(Thread):
    def __init__(self, state, *args, **kwargs):
        super(VMAThread, self).__init__(*args, **kwargs)
        self.state = state

    def run(self):
        while True:
            try:
                self.check_servers_ssh()
                self.get_gpus()
                self.add_vm()
                self.register_vm()
                self.get_vm_ip()
                self.vm_wait_port_is_open()
                self.mount_disk()
                self.check_running_vms()
                self.stop_stale_vm()
                self.stop_vm()
            except Exception as e:
                logger.exception(e)
            time.sleep(10)

    def check_servers_ssh(self):
        with self.state.lock:
            servers = Server.objects.filter(active=True)
            servers_message = {"OK": [], "Failed": []}
            server = None
            for x in servers:
                if x.id not in self.state.servers_in_progress:
                    self.state.servers_in_progress.add(x.id)
                    server = x
                    break
            if server is None:
                return

        status = wait_port_is_open(server.ip, 22)
        server.refresh_from_db()
        send_message_status = False
        if not status and not server.in_error_state:
            server.in_error_state = True
            server.state_message = f"ESX with ip {server.ip} is down"
            server.save()
            send_message_status = True
        elif status and server.in_error_state:
            server.in_error_state = False
            server.state_message = f"ESX with ip {server.ip} is ok"
            server.save()
            send_message_status = True
        with self.state.lock:
            self.state.servers_in_progress.remove(server.id)
        
        if send_message_status:
            self.__send_servers_statuses_to_slack(servers_message)
        
    def __send_servers_statuses_to_slack(self, servers_message):
        servers = Server.objects.filter(active=True)
        for server in servers:
            if server.in_error_state == True:
                servers_message["Failed"].append(server.ip)
            else:
                servers_message["OK"].append(server.ip)
        send_text(text=f"VMAuto: {get_vma_host_name()}\n" +
                        json.dumps(servers_message))

    def get_gpus(self):
        server = None
        with self.state.lock:
            servers = Server.objects.filter(active=True,
                                            in_error_state=False).annotate(number_of_gpus=Count('gpu')).filter(number_of_gpus=0)
            for x in servers:
                if x.id not in self.state.servers_in_progress:
                    self.state.servers_in_progress.add(x.id)
                    server = x
                    break
            if server is None:
                return

        vma = choose_automation(server)
        gpus = vma.get_gpus_data()
        vma.close()

        with self.state.lock:
            for pci_address in gpus:
                gpu = GraphicsProcessingUnit(server=server,
                                            pci_address=pci_address,
                                            device_id=gpus[pci_address]["deviceId"],
                                            vendor_id=gpus[pci_address]["vendorId"])
                gpu.save()
            self.state.servers_in_progress.remove(server.id)

    def add_vm(self):
        start_limit = settings.START_LIMIT
        parallel_start_limit = settings.PARALLEL_START_LIMIT
        with self.state.lock:
            free_and_running = VirtualMachine.objects.filter(used=False, ge_has_started=True).count()
            starting = VirtualMachine.objects.filter(ge_has_started=False, in_error_state=False).count()
            testing_servers = Server.objects.filter(in_test_mode=True, active=True).exists()
            if free_and_running + starting >= start_limit or starting >= parallel_start_limit:
                if not testing_servers:
                    return

            with transaction.atomic():
                free_gpus = GraphicsProcessingUnit.objects.select_for_update().filter(vm__isnull=True,
                                                                                    active=True,
                                                                                    server__active=True,
                                                                                    server__in_error_state=False)
                if free_gpus.filter(server__in_test_mode=True).exists():
                    free_gpu = free_gpus.filter(server__in_test_mode=True).first()
                elif testing_servers:
                    return
                else:
                    free_gpu = free_gpus.first()
                if free_gpu:
                    vm = VirtualMachine(server=free_gpu.server,
                                        dir_name="win_" + str(uuid.uuid4()))
                    vm.save()
                    free_gpu.vm = vm
                    free_gpu.save()
            return

    def register_vm(self):
        vm = None
        with self.state.lock:
            vms = VirtualMachine.objects.filter(vm_id__isnull=True, terminating=False, in_error_state=False)
            for x in vms:
                if x.id not in self.state.vms_in_progress:
                    self.state.vms_in_progress.add(x.id)
                    vm = x
                    break
            if vm is None:
                return

        vma = choose_automation(vm.server)
        vma.make_vm_env(vm)
        
        vm_id, image_name = vma.register_vm(vm)
        vm.vm_id = vm_id
        vma.start_vm(vm)
        vma.close()

        with self.state.lock:
            vm.refresh_from_db()
            vm.vm_id = vm_id
            vm.image_name = image_name
            vm.save()
            self.state.vms_in_progress.remove(vm.id)

    def get_vm_ip(self):
        vm = None
        with self.state.lock:
            vms = VirtualMachine.objects.filter(vm_id__isnull=False, ip__isnull=True, terminating=False, in_error_state=False)
            for x in vms:
                if x.id not in self.state.vms_in_progress:
                    self.state.vms_in_progress.add(x.id)
                    vm = x
                    break
            if vm is None:
                return

        vma = choose_automation(vm.server)
        vm_ip = vma.get_vm_ip(vm)
        vma.close()

        with self.state.lock:
            vm.refresh_from_db()
            if vm_ip is not None:
                vm.ip = vm_ip
            else:
                vm.in_error_state = True
                vm.error_message = "Cannot obtain IP"
            vm.save()
            self.state.vms_in_progress.remove(vm.id)

    def vm_wait_port_is_open(self):
        vm = None
        with self.state.lock:
            vms = VirtualMachine.objects.filter(ip__isnull=False, ge_has_started=False, terminating=False, in_error_state=False)
            for x in vms:
                if x.id not in self.state.vms_in_progress:
                    self.state.vms_in_progress.add(x.id)
                    vm = x
                    break
            if vm is None:
                return

        ge_port_is_open, diag_output, test_screenshot_data = get_diagnostic(vm)

        with self.state.lock:
            vm.refresh_from_db()
            vm.ge_has_started = ge_port_is_open
            if not ge_port_is_open:
                vm.in_error_state = True
                vm.error_message = "Experience has not started after a timeout"
            elif test_screenshot_data is None:
                vm.in_error_state = True
                vm.error_message = "Cannot take test screenshot"
            elif diag_output is None:
                vm.in_error_state = True
                vm.error_message = "Cannot run diagnostic tool"
            else:
                vm.diag_output = diag_output
                with tempfile.NamedTemporaryFile() as temp:
                    temp.write(test_screenshot_data)
                    temp.flush()
                    django_file = File(open(temp.name, 'rb'))
                    vm.test_screenshot.save(vm.dir_name + ".png", django_file, save=True)
            vm.time_of_last_test = timezone.now()            
            vm.save()
            self.state.vms_in_progress.remove(vm.id)

    def mount_disk(self):
        vm = None
        with self.state.lock:
            vms = VirtualMachine.objects.filter(
                application__isnull=False, is_image_mounted=False, in_error_state=False)
            for x in vms:
                if x.id not in self.state.vms_in_progress:
                    self.state.vms_in_progress.add(x.id)
                    vm = x
                    break
            if vm is None:
                return
        
        vma = choose_automation(vm.server)
        vma.mount_disk(vm)
        vma.close()

        with self.state.lock:
            vm.refresh_from_db()
            vm.is_image_mounted = True
            vm.save()
            self.state.vms_in_progress.remove(vm.id)

    def check_running_vms(self):
        vm = None
        with self.state.lock:
            vms = VirtualMachine.objects.filter(ge_has_started=True,
                terminating=False, in_error_state=False, used=False,
                time_of_last_test__lt=timezone.now()-timedelta(minutes=settings.TIME_BETWEEN_VM_CHECKS))
            for x in vms:
                if x.id not in self.state.vms_in_progress:
                    self.state.vms_in_progress.add(x.id)
                    vm = x
                    break
            if vm is None:
                return
            vm.used = True
            vm.save()

        ge_port_is_open, diag_output, test_screenshot_data = get_diagnostic(vm)

        with self.state.lock:
            vm.refresh_from_db()
            if (not ge_port_is_open) or (test_screenshot_data is None) or (diag_output is None):
                vm.terminating = True
                vm.in_error_state = True
            else:
                vm.diag_output = diag_output
                with tempfile.NamedTemporaryFile() as temp:
                    temp.write(test_screenshot_data)
                    temp.flush()
                    django_file = File(open(temp.name, 'rb'))
                    vm.test_screenshot.save(vm.dir_name + ".png", django_file, save=True)
            vm.time_of_last_test = timezone.now()
            vm.used = False
            vm.save()
            self.state.vms_in_progress.remove(vm.id)

    def stop_stale_vm(self):
        with self.state.lock:
            vms = VirtualMachine.objects.filter(used=True, terminating=False,
                                                keep_used_alive__lt=timezone.now()-timedelta(minutes=4))
            vm = None
            for x in vms:
                if x.id not in self.state.vms_in_progress:
                    vm = x
                    break
            if vm is None:
                return
            with transaction.atomic():
                try:
                    vm = VirtualMachine.objects.select_for_update().get(id=vm.id)
                    vm.terminating = True
                    vm.save()
                except VirtualMachine.DoesNotExist:
                    pass

    def stop_vm(self):
        vm = None
        with self.state.lock:
            vms = VirtualMachine.objects.filter(terminating=True)
            for x in vms:
                if x.id not in self.state.vms_in_progress:
                    self.state.vms_in_progress.add(x.id)
                    vm = x
                    break
            if vm is None:
                return

        if vm.vm_id is not None:
            vma = choose_automation(vm.server)
            try:
                vma.stop_vm(vm)
                vma.unregister_vm(vm)
                vma.remove_vm_env(vm)
            except (AutomationStepFailedException, TIMEOUT) as e:
                vm.in_error_state = True
                vm.error_message = str(e)
            vma.close()

        with self.state.lock:
            if vm.in_error_state:
                vm.save()
            else:
                vm.test_screenshot.delete(save=True)
                vm.delete()
            self.state.vms_in_progress.remove(vm.id)



class Command(BaseCommand):
    def handle(self, *args, **options):
        exitcode = None
        while exitcode == 1 or exitcode is None:
            child_process = Process(target=self.run)
            child_process.daemon = True
            child_process.start()
            child_process.join()
            exitcode = child_process.exitcode

    def run(self):
        state = State()
        threads = []
        for i in range(settings.VMAUTO_WORKER_THREADS):
            threads.append(VMAThread(state))
        for thread in threads:
            thread.daemon = True
            thread.start()
        while True:
            for thread in threads:
                thread.join(settings.VMAUTO_WORKER_THREADS)
                if not thread.is_alive():
                    logger.error('One of threads exited - terminate and restart')
                    sys.exit(1)

