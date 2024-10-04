// script.js

document.getElementById('sendButton').addEventListener('click', sendMessage);
document.getElementById('userInput').addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const input = document.getElementById('userInput');
    const messageText = input.value.trim(); // Get input value and trim whitespace

    if (messageText === '') return; // Do nothing if input is empty

    // Create user message element
    const userMessage = document.createElement('div');
    userMessage.classList.add('message', 'user-message');
    userMessage.textContent = messageText;

    // Append user message to messages area
    document.getElementById('messages').appendChild(userMessage);

    // Clear input
    input.value = '';

    // Scroll to the bottom
    scrollToBottom();

    // Simulate a bot response after a short delay
    setTimeout(() => {
        const botMessage = document.createElement('div');
        botMessage.classList.add('message', 'bot-message');
        botMessage.textContent = "This is a bot response."; // Change this to your bot response

        // Append bot message to messages area
        document.getElementById('messages').appendChild(botMessage);

        // Scroll to the bottom
        scrollToBottom();
    }, 1000);
}

function scrollToBottom() {
    const messages = document.getElementById('messages');
    messages.scrollTop = messages.scrollHeight; // Scroll to the bottom of the messages area
}
