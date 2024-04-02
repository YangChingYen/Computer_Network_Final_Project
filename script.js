const serverUrl = 'http://127.0.0.1:7831/'
function showRegisterForm() {
  document.getElementById("loginForm").classList.add("hidden");
  document.getElementById("registerForm").classList.remove("hidden");
}

function showLoginForm() {
  document.getElementById("loginForm").classList.remove("hidden");
  document.getElementById("registerForm").classList.add("hidden");
}

function login() {
  const account = document.getElementById("account").value;
  const password = document.getElementById("password").value;
  
  // Handle login logic (e.g., send data to server)
  console.log("Login clicked. Account:", account, "Password:", password);

  const url = `${serverUrl}login`;
  const data = { account, password };

  // Send POST request with account and password in the request body
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => response.text())
    .then(data => {
      console.log('Server response:', data);

      if (data.trim() === "1") {
        // Successful login
        alert('Login successful!');
        showMessageBoard();
        fetchMessageHistory();
        // You can perform additional actions for authenticated users here
      } else {
        // Failed login
        alert('Login failed. Please check your credentials.');
      }
    })
    .catch(error => {
      console.error('Error:', error.message);
    });

}

function register() {
  const newAccount = document.getElementById("newAccount").value;
  const newPassword = document.getElementById("newPassword").value;
  
  const url = `${serverUrl}register`;
  const data = { newAccount, newPassword };

  // Send POST request with new account and password in the request body
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
    .then(response => response.text())
    .then(data => {
      console.log('Server response:', data);

      if (data.trim() === "1") {
        // Successful registration
        alert('Registration successful!');
        showMessageBoard();
        fetchMessageHistory();
      } else {
        // Failed registration
        alert('Registration failed. Please try again.');
      }
    })
    .catch(error => {
      console.error('Error:', error.message);
    });
  // Handle registration logic (e.g., send data to server)
  console.log("Register clicked. New Account:", newAccount, "New Password:", newPassword);
}

function showMessageBoard() {
  document.getElementById("loginForm").classList.add("hidden");
  document.getElementById("registerForm").classList.add("hidden");
  document.getElementById("messageBoard").classList.remove("hidden");
}

function formatAMPM(date) {
  let hours = date.getHours();
  let minutes = date.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';

  hours %= 12;
  hours = hours ? hours : 12; // Handle midnight as 12 AM

  minutes = minutes < 10 ? '0' + minutes : minutes;

  return `${hours}:${minutes} ${ampm}`;
}

function sendMessage() {
  const messageInput = document.getElementById("messageInput");
  const message = messageInput.value;

  if (message.trim() === "") {
      // Don't send empty messages
      return;
  }
  const messageType = "Text"; // You can change this based on the actual message type
  const date = new Date();
  const formattedDate = `${date.getMonth() + 1}/${date.getDate()} ${formatAMPM(date)}`;

  const url = `${serverUrl}sendMessage`;
  const data = {
    message,
    type: messageType,
    date: formattedDate,
  };

  // Send POST request with the message in the request body
  fetch(url, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
  })
  .then(response => response.text())
  .then(data => {
    if (data.trim() === "1") {
      console.log('Server response:', data);
      alert("Sucessfully posted!");
      fetchMessageHistory();
    }
    else {
      alert("Post message failed");
    }
      
      // Handle the server response if needed
  })
  .catch(error => {
      console.error('Error:', error.message);
  });

  // Clear the input field after sending the message
  messageInput.value = "";
}

function uploadAudio() {
  const audioInput = document.getElementById("audioInput");
  
  if (audioInput.files.length === 0) {
      // No file selected
      return;
  }

  const audioFile = audioInput.files[0];
  const formData = new FormData();
  formData.append("audio", audioFile);

  const uploadUrl = `${serverUrl}upload_audio`;

  // Send POST request with the audio file in the request body
  fetch(uploadUrl, {
      method: 'POST',
      body: formData,
  })
  .then(response => response.text())
  .then(data => {
      console.log('Server response:', data);

      // After uploading the audio, update the message board
      if (data.trim() === "1") {
        console.log('Server response:', data);
        alert("Sucessfully posted!");
        fetchMessageHistory();
      }
      else {
        alert("Post message failed");
      }
  })
  .catch(error => {
      console.error('Error:', error.message);
  });
}

function uploadVideo() {
  const videoInput = document.getElementById("videoInput");
  const videoFile = videoInput.files[0];

  // Create a FormData object to send the file to the server
  const formData = new FormData();
  formData.append("videoFile", videoFile);

  // Send a POST request to the server to handle video file upload
  fetch(`${serverUrl}upload_video`, {
      method: 'POST',
      body: formData,
  })
  .then(response => response.text())
  .then(data => {
      console.log('Server response:', data);
      // Handle the server response if needed
      if (data.trim() === "1") {
        console.log('Server response:', data);
        alert("Sucessfully posted!");
        fetchMessageHistory();
      }
      else {
        alert("Post message failed");
      }
  })
  .catch(error => {
      console.error('Error:', error.message);
  });
}

function fetchMessageHistory() {
  const url = `${serverUrl}message_board`;

  fetch(url)
    .then(response => response.text())
    .then(data => {
      // Process and display the message history on the client side
      displayMessageHistory(data);
    })
    .catch(error => {
      console.error('Error fetching message history:', error.message);
    });
}

function displayMessageHistory(message) {
  const messagesDiv = document.getElementById("messages");

  // Split the message history string into an array of messages
  const messagesArray = message.split('\n');

  // Clear the existing messages
  messagesDiv.innerHTML = "";

  // Loop through each message and display it
  for (const messageString of messagesArray) {
      // Split the message string into an array of message components
      const messageComponents = messageString.split('$$$');

      // Ensure the message has the expected number of components
      if (messageComponents.length == 4) {
          // Extract the relevant components
          const messageContent = messageComponents[1];
          const messageType = messageComponents[2];
          const messageDate = messageComponents[3];

          // Create a message element
          const messageElement = document.createElement("p");
          if (messageType === "Text") {
            // For text messages
            messageElement.innerHTML = `<span style="border:3px purple solid;border-radius: 5px;display:block;font-size: 35px;">${messageContent}</span> <span style="font-size: smaller;float:right;">${messageDate}</span>`;
          } else if (messageType === "Audio") {
            // For audio messages
            // You need to implement the logic to fetch and display audio based on messageContent (audio file id)
            messageElement.innerHTML = `<span style="border:3px purple solid;border-radius: 5px;display:block;font-size: 35px;"><audio controls><source src="${serverUrl}getAudio?id=${messageContent}" type="audio/mpeg"></audio></span> <span style="font-size: smaller;float:right;">${messageDate}</span>`;
          } else if (messageType === "Video") {
            // Handle other message types here
            messageElement.innerHTML = `<span style="border:3px purple solid;border-radius: 5px;display:block;font-size: 35px;"><video width="320" height="240" controls><source src="${serverUrl}getVideo?id=${messageContent}" type="video/mp4"></video></span> <span style="font-size: smaller;float:right;">${messageDate}</span>`
          }
          // Add the message element to the messages container
          messagesDiv.appendChild(messageElement);
      }
  }
}


