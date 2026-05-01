document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter") sendMessage();
});

function sendMessage() {
    const inputField = document.getElementById("user-input");
    const message = inputField.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    inputField.value = "";

    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => appendMessage(data.reply, "bot"))
    .catch(err => appendMessage("Something went wrong...", "bot"));
}

function appendMessage(text, sender) {
    const chatWindow = document.getElementById("chat-window");
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerText = text;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
