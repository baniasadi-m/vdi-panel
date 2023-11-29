function copyText(elementId) {
    // Get the text content of the element with the specified ID
    var textToCopy = document.getElementById(elementId).innerText;

    // Create a temporary textarea element to copy the text to the clipboard
    var tempTextarea = document.createElement('textarea');
    tempTextarea.value = textToCopy;

    // Append the textarea to the document
    document.body.appendChild(tempTextarea);

    // Select the text inside the textarea
    tempTextarea.select();
    tempTextarea.setSelectionRange(0, 99999); /* For mobile devices */

    // Copy the selected text to the clipboard
    document.execCommand('copy');

    // Remove the temporary textarea
    document.body.removeChild(tempTextarea);
    // Show temporary message
    showTempMessage('Text Copied', 2000);
  }
  function showTempMessage(message, duration) {
    var tempMessageElement = document.getElementById('tempMessage');
    tempMessageElement.innerText = message;
    tempMessageElement.style.display = 'block';

    // Hide the message after the specified duration
    setTimeout(function() {
      tempMessageElement.style.display = 'none';
    }, duration);
  }