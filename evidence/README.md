Evidence
Purpose

This folder contains all supporting evidence (screenshots, configuration exports, logs, and other artifacts) referenced throughout the project documentation. It serves as a central repository for UI screenshots, AWS console captures (API Gateway, Lambda, DynamoDB, etc.), IAM policy JSON files, CloudWatch log/metrics exports, and other raw files that validate and illustrate the implementation and results discussed in the documentation.

Frontend

01 Upload Form – Screenshot of the web application’s file upload form interface where a user selects a document to upload.


02 Success Toast – Screenshot showing the success notification (toast message) confirming a document was uploaded successfully.


API Gateway

03 API Gateway Routes – Screenshot of the API Gateway console showing the configured REST API endpoints (e.g. the POST /receipt route and any other routes) and their integration settings.


Lambda

04 Lambda Function Configuration – Screenshot of the AWS Lambda function’s details in the console (configuration and code section), showing settings like the runtime, environment variables, and trigger (linked API Gateway).


IAM

Lambda Execution Policy – infra/policy_post_lambda.json – IAM policy file attached to the “PostReceipt” Lambda function’s role, granting it permissions (e.g. to write to DynamoDB, put objects to S3, etc.).

Search Function Policy – infra/policy_search_lambda.json – IAM policy file for the “SearchReceipts” Lambda (or similar), granting read/query access to the DynamoDB table for retrieval operations.

(IAM policy JSON files are stored in the infra/ subfolder.)

DynamoDB

05 DynamoDB Table Record – Screenshot of the DynamoDB console showing a record in the application’s table (e.g. a stored receipt item with its ID, vendor, date, total, and items fields).


CloudWatch (Logs Insights, Metrics, Alarms)

06 CloudWatch Logs Insights Query – Screenshot of a CloudWatch Logs Insights query results page, filtering log events for the phrase “Inserted successfully” to confirm that insert operations are logged as expected (shows timestamps and log messages for successful inserts).


07 CloudWatch Metrics Dashboard – Screenshot of the CloudWatch metrics dashboard showing custom application metrics InsertSuccess and InsertError after a test run. This illustrates that InsertSuccess incremented (on a successful insert) while InsertError remained zero, confirming the system’s behavior.


08 InsertError Alarm Detail – Screenshot of the CloudWatch alarm configuration for InsertErrorAlarm (threshold set to trigger if ≥1 error occurs within 5 minutes). Shows the alarm details page including its threshold and SNS notification setup.


09 InsertSuccess Alarm Detail – Screenshot of the CloudWatch alarm configuration for InsertSuccessAlarm (triggers if there are 0 successful inserts in a 15-minute window, indicating a potential pipeline stall). Shows the alarm’s threshold and actions.


10 CloudWatch Alarms List – Screenshot of the CloudWatch Alarms dashboard listing all configured alarms (e.g. both InsertErrorAlarm and InsertSuccessAlarm) and their current state/status.


Alarm Configuration (JSON) – logs/insert_error_alarm.json – Exported JSON configuration for the InsertError CloudWatch alarm (includes its name, metric target, threshold, evaluation periods, and actions).

Logs Export (Text) – logs/cloudwatch_logs_export.txt – Text export of sample CloudWatch log events captured during testing (for example, raw log lines showing a successful insert operation and any associated info or error messages).

(The alarm JSON and log text files are stored in the logs/ subfolder.)

AWS X-Ray

11 X-Ray Traces List – Screenshot of the AWS X-Ray console showing a list of recent trace records. It includes individual request traces with details like timestamps, durations, and HTTP status codes, which helps in verifying end-to-end request performance.


12 X-Ray Service Map – Screenshot of the AWS X-Ray service map, providing a visual representation of the system’s architecture in real time. It displays the connections between components (API Gateway, Lambda, DynamoDB, etc.) and highlights performance (latencies) and error rates, confirming that all services are interacting as expected.


Postman (API Testing)

13 Postman Request Setup – Screenshot of the Postman client showing the configuration for a POST request to the API (endpoint URL, required headers like Content-Type and any auth keys, and a sample JSON body for a receipt). This demonstrates how the API was invoked during testing.


14 Postman Response (200 OK) – Screenshot of Postman’s response panel after a successful POST /receipt request, showing a 200 OK status and the returned JSON body (including a confirmation message and a generated receiptId). This confirms the API call succeeded and returned the expected output.


Architecture Diagram

15 System Architecture Diagram – Diagram illustrating the overall system architecture and component interactions. It shows how the frontend, API Gateway, Lambda functions, DynamoDB, and other services (like S3, CloudWatch, X-Ray) are connected. This diagram provides a high-level overview of the solution’s design and data flow.


Demo (GIF/MP4)

16 Application Demo – An animated demonstration of the application in action (user perspective). This GIF/video shows the end-to-end flow: a user uploading a document via the frontend, the request being processed through the AWS backend (triggering Lambda and other services), and the resulting output or confirmation being displayed. It highlights key features and verifies the system working as intended.


(For video format, see 16_application_demo.mp4 in this folder.)
