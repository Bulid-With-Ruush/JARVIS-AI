
const messages = document.getElementById("messages");
const input = document.getElementById("command");
const core = document.getElementById("core");
const coreStatus = document.getElementById("coreStatus");
const voiceButton = document.getElementById("voice");

const BACKEND = "http://127.0.0.1:8765";

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = "message " + type;

  const label = document.createElement("small");
  label.textContent = type === "bot" ? "ZENOX" : "YOU";

  div.appendChild(label);
  div.appendChild(document.createTextNode(text));
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;

  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 0.9;

  speechSynthesis.speak(utterance);
}

async function sendCommand() {
  const command = input.value.trim();
  if (!command) return;

  addMessage(command, "user");
  input.value = "";
  coreStatus.textContent = "PROCESSING...";

  try {
    const response = await fetch(BACKEND + "/command", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ command })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }

    addMessage(data.reply, "bot");
    speak(data.reply);
    coreStatus.textContent = "RESPONSE GENERATED";

  } catch (error) {
    addMessage(
      "I cannot connect to my PC backend. Please start ZENOX on your computer first.",
      "bot"
    );
    coreStatus.textContent = "BACKEND OFFLINE";
  }
}

document.getElementById("send").addEventListener("click", sendCommand);

input.addEventListener("keydown", event => {
  if (event.key === "Enter") sendCommand();
});

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.interimResults = false;

  recognition.onstart = () => {
    core.classList.add("listening");
    coreStatus.textContent = "LISTENING...";
    voiceButton.classList.add("active");
    voiceButton.textContent = "● LISTENING — SPEAK NOW";
  };

  recognition.onresult = event => {
    input.value = event.results[0][0].transcript;
    sendCommand();
  };

  recognition.onerror = event => {
    coreStatus.textContent = "VOICE ERROR: " + event.error;
  };

  recognition.onend = () => {
    core.classList.remove("listening");
    voiceButton.classList.remove("active");
    voiceButton.textContent = "🎙 ACTIVATE VOICE";

    if (coreStatus.textContent === "LISTENING...") {
      coreStatus.textContent = "AWAITING COMMAND";
    }
  };

  voiceButton.addEventListener("click", () => {
    try {
      recognition.start();
    } catch (error) {
      coreStatus.textContent = "PLEASE WAIT";
    }
  });
} else {
  voiceButton.textContent = "VOICE NOT SUPPORTED";
  voiceButton.disabled = true;
}
