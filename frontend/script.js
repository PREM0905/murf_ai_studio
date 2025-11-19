// ----------------------------
// SELECT UI ELEMENTS
// ----------------------------
const micBtn = document.getElementById("micBtn");
const statusEl = document.getElementById("status");
const messagesEl = document.getElementById("messages");
const reactorWrapper = document.querySelector(".reactor-wrapper");

let mediaRecorder;
let audioChunks = [];

// ----------------------------
// INITIALIZE MICROPHONE
// ----------------------------
async function initRecorder() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (e) => {
            audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            statusEl.innerText = "PROCESSING REQUEST...";

            const blob = new Blob(audioChunks, { type: "audio/wav" });
;
            audioChunks = [];

            appendMessage("Voice Input Received", "msg-user");

            const fd = new FormData();
            fd.append("audio", blob, "recording.webm");

            try {
                const res = await fetch("http://127.0.0.1:5000/asr", {
                    method: "POST",
                    body: fd
                });

                const data = await res.json();

                if (!data.ok) {
                    appendMessage("❌ Error: " + data.error, "msg-bot");
                    statusEl.innerText = "STUDIO READY";
                    stopSpeakingAnimation();
                    return;
                }

                appendMessage("You: " + data.transcript, "msg-user");
                
                // Handle maps responses
                let processedReply = data.reply;
                if (typeof handleMapsResponse === 'function') {
                    processedReply = handleMapsResponse(data.reply);
                }
                
                appendMessage("AI: " + processedReply, "msg-bot");

                const audioSrc = "data:audio/wav;base64," + data.audio_base64;
                const audio = new Audio(audioSrc);

                startSpeakingAnimation();
                audio.onended = () => {
                    stopSpeakingAnimation();
                    statusEl.innerText = "STUDIO READY";
                };

                await audio.play();

            } catch (err) {
                appendMessage("⚠ Network Error: " + err.message, "msg-bot");
                stopSpeakingAnimation();
            }
        };

        statusEl.innerText = "STUDIO READY";

    } catch (err) {
        statusEl.innerText = "AUDIO ACCESS DENIED";
    }
}

// ----------------------------
// UI ANIMATIONS
// ----------------------------
function startSpeakingAnimation() {
    reactorWrapper.classList.add("reacting");
}

function stopSpeakingAnimation() {
    reactorWrapper.classList.remove("reacting");
}

// ----------------------------
// APPEND MESSAGE
// ----------------------------
function appendMessage(text, type) {
    const div = document.createElement("div");
    div.className = "message " + type;
    div.innerText = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

// ----------------------------
// MIC EVENTS
// ----------------------------
micBtn.addEventListener("mousedown", () => {
    audioChunks = [];
    mediaRecorder.start();
    statusEl.innerText = "LISTENING...";
    startSpeakingAnimation();
});

micBtn.addEventListener("mouseup", () => {
    mediaRecorder.stop();
    stopSpeakingAnimation();
});

micBtn.addEventListener("touchstart", (e) => {
    e.preventDefault();
    audioChunks = [];
    mediaRecorder.start();
    statusEl.innerText = "LISTENING...";
    startSpeakingAnimation();
});

micBtn.addEventListener("touchend", (e) => {
    e.preventDefault();
    mediaRecorder.stop();
    stopSpeakingAnimation();
});

// ----------------------------
// START
// ----------------------------
initRecorder();
