# Frontend Integration Deep Dive

## Frontend Integration Overview

The **React frontend** of the IntelliDoc Engine provides an intuitive interface for users to submit receipt data to the backend for processing. It serves as the entry point where users upload receipt images or enter receipt details, which are then sent via a **POST** request to the backend’s **API Gateway** endpoint. This integration allows the frontend to hand off data to serverless backend components (like AWS Lambda and Textract) for analysis. In summary, the React app gathers user input (receipt image/text) and **sends it to the backend** over HTTP, then handles the response to give feedback to the user.

---

## React Upload Form

The upload form in the React application lets users provide the necessary receipt information and initiate processing. The form includes the following elements:

* **File input** – A file picker for the user to select a receipt image (e.g. a photo or PDF of a receipt). After a file is chosen, the app may display the file name to confirm the selection.
* **Textarea for receipt** – A multiline text field where the user can type or paste receipt text. This can be used for additional notes or to input receipt details directly (for example, if an image is unavailable).
* **Submit button** – A button that, when clicked, triggers the form submission. The app will gather the selected file and text input, then send them to the backend for processing.

🖼️ **Screenshot 1: React upload form UI** – *The upload form in the IntelliDoc React frontend, showing the file picker, text area for receipt details, and the submit button.*

When the user clicks the **Submit** button, the form’s data is packaged and sent to the backend. The React app typically disables the form during upload and might show a loading indicator (to prevent multiple submissions) while waiting for the server’s response.

---

## API Calls (POST /receipt)

On form submission, the React app performs an **API call** to the backend to upload the receipt data. This is done via a **POST** request to the API Gateway endpoint (e.g. `POST /receipt`). Under the hood, the app uses the browser’s **Fetch API** (or an HTTP client like Axios) to send the request. The receipt data (both the file and any text from the textarea) is sent in the request body. Typically, a **FormData** object is used to combine the file and text into a multi-part form payload that the backend can parse.

For example, the React code may create a FormData and use `fetch()` as follows:

```jsx
// Prepare form data payload
const formData = new FormData();
formData.append('file', selectedFile);        // the file from the file input
formData.append('text', receiptText);         // the text from the textarea

// Send POST request to backend API endpoint
fetch('<API_GATEWAY_URL>/receipt', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => {
    console.log('Upload successful:', data);
    // (Success handling shown below)
  })
  .catch(error => {
    console.error('Upload error:', error);
    // (Error handling shown below)
  });
```

In this snippet, the frontend appends the chosen file and text input into a FormData. The **API Gateway endpoint** URL (represented by `<API_GATEWAY_URL>/receipt`) is the address of the backend’s receipt ingestion API. The fetch call sends an HTTP POST to that URL with the form data. No manual content-type header is set in this case because the browser will automatically set the appropriate **multipart/form-data** headers for the FormData request.

🖼️ **Screenshot 2: Browser DevTools – POST /receipt** – *Developer Tools Network panel showing the POST request to the `/receipt` endpoint. The payload includes the uploaded file and text fields, confirming the frontend is sending the data correctly.*

When the request is sent, the backend (via API Gateway and a Lambda function) will process the receipt. The React app waits for a response. A successful response (HTTP 200 OK) indicates the receipt was ingested and processed, whereas an error status would indicate something went wrong (such as a validation error or server issue). The frontend handles each case to give feedback to the user.

---

## Success Feedback with Toast

After a successful upload, the React app provides feedback to the user through a **toast notification**. The app displays a green success toast message to confirm that the receipt was submitted and processed successfully. This is implemented using a toast utility (for example, **React-Toastify** or a similar library) that creates a small popup message on the screen.

In the code, once the POST request completes with a success status, the app triggers a toast. For instance, using React-Toastify the code might look like:

```jsx
// Inside the .then handler for a successful fetch:
toast.success('Receipt uploaded successfully!', {
  position: 'top-right',
  autoClose: 5000,  // toast automatically closes after 5 seconds
  hideProgressBar: false,
  pauseOnHover: true,
  theme: 'colored'
});
```

This code displays a brief, non-intrusive message to the user. The toast is typically styled in green (to indicate success) and appears at the top-right corner of the page. It might say something like “Receipt uploaded successfully!” or “✅ Your receipt has been received.” The user can continue using the app, as the toast will disappear after a short delay.

🖼️ **Screenshot 3: Success toast message after submit** – *A green success toast is shown in the React app, confirming to the user that the receipt was uploaded and processed without issues.*

In addition to showing a toast, the frontend may also reset the form (e.g. clear the file input and text area) to prepare for the next upload. This gives the user clear visual confirmation that the operation succeeded and the form is ready for new input.

---

## Error Handling

Proper error handling ensures the user is notified if something goes wrong during the upload. If the API call fails – for example, due to a network issue or a server-side error – the React app will catch the error and display an error toast notification (often styled in red) to alert the user.

In the fetch call, a `.catch` block (or an `async/await` try-catch) is used to handle any exceptions or non-OK responses. For instance:

```jsx
fetch('<API_GATEWAY_URL>/receipt', { method: 'POST', body: formData })
  .then(response => {
    if (!response.ok) {
      // If HTTP status is not ok (e.g. 4xx or 5xx), throw an error to be caught below
      throw new Error('Server responded with an error!');
    }
    return response.json();
  })
  .then(data => {
    // handle success (as shown above)
  })
  .catch(error => {
    console.error('Error submitting receipt:', error);
    toast.error('Failed to upload receipt. Please try again.');
  });
```

In the code above, any error or non-200 response will trigger the `catch` block. Inside the catch, the app logs the error (for debugging purposes) and then shows an **error toast** to the user. The toast might display a message like “Failed to upload receipt. Please try again.” to inform the user that their submission did not go through. This error toast is typically styled in red or with an error icon, making it distinct from the success message.

The React frontend’s error handling ensures that users receive immediate feedback in case of issues. The form might also be re-enabled so the user can correct the problem (for example, check their internet connection or verify the file) and attempt to submit again. By providing clear error notifications, the application improves user experience even when the backend cannot successfully process a request.
