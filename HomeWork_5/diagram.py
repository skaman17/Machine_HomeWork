# diagram.py
from diagrams import Cluster, Diagram
from diagrams.onprem.monitoring import Prometheus
from diagrams.onprem.monitoring import Grafana
from diagrams.onprem.database import Mysql
from diagrams.onprem.compute import Server


with Diagram("VagrantFile Setup", show=False):
    Internet = Server("Internet")

    with Cluster("VirtualMachine2"):
        Grafana = Grafana("Grafana")
        PrometheusServer = Prometheus("Prometheus")
        AlertManager = Prometheus("Alert Manager")

    with Cluster("VirtualMachine1"):
        MySQL_Exporter = Prometheus("MySL Exporter")
        Node_Exporter = Prometheus("Node Exporter")
        MySQL_Database = Mysql("MySQL Database")
        

        Internet >> Grafana
        Internet >> PrometheusServer
        Grafana >> PrometheusServer
        PrometheusServer >> AlertManager
        AlertManager >> Internet 
        PrometheusServer >> MySQL_Exporter
        PrometheusServer  >> Node_Exporter
        MySQL_Exporter >> MySQL_Database
        
