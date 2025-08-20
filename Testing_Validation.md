# Testing & Validation

**Purpose:** Prove the API works end-to-end by executing real requests and verifying that each component (from request handling to data storage and monitoring) functions correctly.

---

# 🔧 API Testing Setup

## Postman Configuration (URL, Headers, JSON Body)

To test the API's end-to-end functionality, we used Postman to simulate client requests. We configured a new POST request in Postman with the following details:

- **URL:** `https://45002xf9i1.execute-api.us-east-1.amazonaws.com/prod/receipts`
- **Headers:** Included `Content-Type: application/json`
- **Body:** Selected **raw** JSON format and provided a JSON payload representing the receipt data:

```json
{
  "documentName": "receipt1.txt",
  "receiptText": "Milk 2.99, Bread 1.49"
}
📸 Screenshot 1: Postman Request Setup


What this shows:

POST method configuration targeting the correct API Gateway endpoint
Required headers including Content-Type: application/json
JSON body structure with documentName and receiptText fields
Postman interface ready to send the test request
Clean workspace setup for API testing
🚀 API Response Testing
Example POST Request → Response
With Postman configured, we executed the POST request to the /receipts endpoint. The API call succeeded with an HTTP 200 OK response, confirming the request was processed without errors. The response body returned by the API contained a success message and the new receipt ID.

Example response:

json
Copy
{
  "message": "Receipt saved successfully!",
  "receiptId": "receipt1.txt#2025-08-20T08:32:10.6956"
}
Performance Metrics:

Response Time: 565ms (well within acceptable limits)
Response Size: 537 B
Status: 200 OK
Success Rate: 100% during testing
📸 Screenshot 2: Postman Response (200 OK)


What this shows:

Successful HTTP 200 OK response from the API
JSON response body with success message and generated receipt ID
Response time of 565ms indicating good performance
Response size of 537 bytes showing efficient data transfer
Green status indicator confirming successful API call
Complete request/response cycle working as expected
