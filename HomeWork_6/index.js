const express = require('express');
const { v4: uuidv4 } = require('uuid'); // Import the UUID library

const app = express();
const port = process.env.PORT || 3000; // Use the PORT environment variable, default to 3000 if not set.

// Root endpoint
app.get('/', (req, res) => {
  res.send('Hello World!');
});

// Health check endpoint
app.get('/healthz', (req, res) => {
  // Respond with OK or another appropriate message
  res.status(200).send('OK');
});

// UUID generation endpoint
app.get('/uuid', (req, res) => {
  // Generate a new UUID and return it in JSON format
  res.json({ uuid: uuidv4() });
});

// Start the server
app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});

