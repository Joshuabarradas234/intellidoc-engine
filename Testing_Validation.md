# Testing & Validation

**Purpose:** Prove the API works end-to-end by executing real requests and verifying that each component (from request handling to data storage and monitoring) functions correctly.

---

## Postman Setup (URL, Headers, JSON Body)

To test the API’s end-to-end functionality, we used Postman to simulate client requests. We configured a new POST request in Postman with the following details:

- **URL:** The API endpoint for creating a receipt (e.g. the base API URL with the `/receipt` path).
- **Headers:** Included `Content-Type: application/json` (and an API key or authorization header if required).
- **Body:** Selected **raw** JSON format and provided a JSON payload representing the receipt data. For example:

```json
{
  "documentName": "sample-receipt.txt",
  "receiptText": "Woolworths\nDate: 2025-08-13\nTotal: 45.67\n..."
}
Screenshot 1: Postman Request Setup
Shows the POST method, target URL, required headers, and example JSON body configured in Postman.

Example POST Request → Response
With Postman configured, we executed the POST request to the /receipt endpoint. The API call succeeded with an HTTP 200 OK response, confirming the request was processed without errors. The response body returned by the API contained a success message and the new receipt ID.

Example response:

json
Copy
Edit
{
  "message": "Receipt processed successfully",
  "receiptId": "12345abcdef"
}
Screenshot 2: Postman Response (200 OK)
Shows the JSON response in Postman with a success message and receipt ID.

GET/Search Request Example → Response
After inserting a receipt, we tested retrieval by performing a GET request to the search endpoint, e.g.:

bash
Copy
Edit
GET /receipts?query=SuperMart
Example search response:

json
Copy
Edit
[
  {
    "receiptId": "12345abcdef",
    "vendor": "SuperMart",
    "date": "2025-08-13",
    "total": 45.67,
    "items": ["Apples", "Milk", "Bread"]
  }
]
We also tested a direct GET by ID:

bash
Copy
Edit
GET /receipt/12345abcdef
This returned the complete stored receipt record from DynamoDB.

Error Handling Test (Optional)
We verified that the API responds correctly to invalid requests:

Missing Fields: Returns 400 Bad Request with validation error.

Invalid Format: Returns 400 Bad Request if JSON is malformed.

Not Found: Returns 404 Not Found for non-existent receipt IDs.

These checks confirm the API gracefully handles incorrect or unexpected inputs.

Validation in CloudWatch Metrics
The Lambda backend publishes custom metrics to CloudWatch:

InsertSuccess – increments on successful receipt insertions.

InsertError – increments on failed insert attempts.

After our POST request, InsertSuccess increased by 1, and InsertError remained 0, confirming the API worked as expected and monitoring captured the event.

Screenshot 3: CloudWatch Metrics After Test
Shows the CloudWatch dashboard with InsertSuccess incremented and InsertError unchanged after running the Postman test.

Summary:
This testing proves that the API:

Accepts and processes valid requests.

Stores and retrieves data successfully.

Returns correct status codes and messages for errors.

Updates monitoring metrics to reflect operations.

This ensures the system is reliable, verifiable, and ready for real-world use.
