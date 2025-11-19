// STUDIO Dual Interface JavaScript
class STUDIOAssistant {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentMode = 'voice';
        this.ttsEnabled = true;
        this.wakeWordActive = false;
        this.microphoneStream = null;
        this.microphoneGranted = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.requestMicrophonePermission();
    }

    async requestMicrophonePermission() {
        try {
            this.microphoneStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.microphoneGranted = true;
            this.voiceStatus.textContent = 'Microphone ready. Click "Start Listening" for wake word.';
        } catch (error) {
            this.microphoneGranted = false;
            this.voiceStatus.textContent = 'Microphone access denied.';
            this.addMessage('System', 'Microphone access required for voice features.', 'bot');
        }
    }



    initializeElements() {
        // Mode buttons
        this.voiceModeBtn = document.getElementById('voiceMode');
        this.textModeBtn = document.getElementById('textMode');
        
        // Interface panels
        this.voiceInterface = document.getElementById('voiceInterface');
        this.textInterface = document.getElementById('textInterface');
        
        // Voice elements
        this.micButton = document.getElementById('micButton');
        this.reactorCore = document.getElementById('reactorCore');
        this.voiceStatus = document.getElementById('voiceStatus');
        
        // Wake word button
        this.wakeWordBtn = document.createElement('button');
        this.wakeWordBtn.textContent = '🎧 Start Listening';
        this.wakeWordBtn.className = 'wake-word-btn';
        this.wakeWordBtn.style.cssText = 'margin: 10px; padding: 10px 20px; background: #00ff41; color: black; border: none; border-radius: 5px; cursor: pointer;';
        document.querySelector('.reactor-container').appendChild(this.wakeWordBtn);
        
        // Text elements
        this.textInput = document.getElementById('textInput');
        this.sendButton = document.getElementById('sendButton');
        this.enableTTS = document.getElementById('enableTTS');
        
        // Messages
        this.messagesPanel = document.getElementById('messagesPanel');
    }

    setupEventListeners() {
        // Mode switching
        this.voiceModeBtn.addEventListener('click', () => this.switchMode('voice'));
        this.textModeBtn.addEventListener('click', () => this.switchMode('text'));
        
        // Voice interface
        this.micButton.addEventListener('click', () => this.toggleRecording());
        this.wakeWordBtn.addEventListener('click', () => this.toggleWakeWord());
        
        // Text interface
        this.sendButton.addEventListener('click', () => this.sendTextMessage());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendTextMessage();
        });
        this.enableTTS.addEventListener('change', (e) => {
            this.ttsEnabled = e.target.checked;
        });
    }

    switchMode(mode) {
        this.currentMode = mode;
        
        if (mode === 'voice') {
            this.voiceModeBtn.classList.add('active');
            this.textModeBtn.classList.remove('active');
            this.voiceInterface.classList.remove('hidden');
            this.textInterface.classList.add('hidden');
        } else {
            this.textModeBtn.classList.add('active');
            this.voiceModeBtn.classList.remove('active');
            this.textInterface.classList.remove('hidden');
            this.voiceInterface.classList.add('hidden');
            this.textInput.focus();
        }
    }

    async toggleRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }

    async startRecording() {
        if (!this.microphoneGranted) {
            this.addMessage('System', 'Microphone access required.', 'bot');
            return;
        }

        try {
            this.mediaRecorder = new MediaRecorder(this.microphoneStream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processVoiceInput();
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            
            this.micButton.classList.add('recording');
            this.voiceStatus.textContent = 'Listening... Click to stop';
            this.reactorCore.style.animation = 'recordingPulse 0.5s infinite';

        } catch (error) {
            console.error('Error starting recording:', error);
            this.addMessage('System', 'Recording failed.', 'bot');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            this.isRecording = false;
            this.micButton.classList.remove('recording');
            this.voiceStatus.textContent = 'Processing...';
            this.reactorCore.style.animation = '';
        }
    }

    async processVoiceInput() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob);

        try {
            const response = await fetch('http://127.0.0.1:5000/asr', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.ok) {
                this.addMessage('You', data.transcript, 'user');
                this.addMessage('STUDIO', data.reply, 'bot');
                
                // Handle navigation/search redirect
                console.log('Voice response:', data);
                if (data.navigation && data.navigation.redirect_url) {
                    console.log('Voice navigation redirect:', data.navigation.redirect_url);
                    setTimeout(() => {
                        const opened = window.open(data.navigation.redirect_url, '_blank');
                        if (!opened) console.log('Popup blocked - voice navigation');
                    }, 1000);
                } else if (data.search && data.search.redirect_url) {
                    console.log('Voice search redirect:', data.search.redirect_url);
                    setTimeout(() => {
                        const opened = window.open(data.search.redirect_url, '_blank');
                        if (!opened) {
                            console.log('Popup blocked - trying location.href');
                            window.location.href = data.search.redirect_url;
                        }
                    }, 1000);
                } else if (data.music && data.music.redirect_url) {
                    console.log('Voice music redirect:', data.music.redirect_url);
                    setTimeout(() => {
                        // Open music player (handles both Spotify and YouTube)
                        window.open(data.music.redirect_url, '_blank');
                    }, 1000);
                } else {
                    console.log('No voice redirect found');
                }
                
                // Play TTS audio
                if (data.audio_base64) {
                    this.playAudio(data.audio_base64);
                }
            } else {
                this.addMessage('System', data.error || 'Failed to process voice input', 'bot');
            }

        } catch (error) {
            console.error('Error processing voice:', error);
            this.addMessage('System', `Network error: ${error.message}. Make sure Flask server is running on port 5000.`, 'bot');
        }

        this.voiceStatus.textContent = 'Click microphone to speak';
    }

    async sendTextMessage() {
        const message = this.textInput.value.trim();
        if (!message) return;

        this.addMessage('You', message, 'user');
        this.textInput.value = '';

        try {
            const response = await fetch('http://127.0.0.1:5000/text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    tts_enabled: this.ttsEnabled
                })
            });

            const data = await response.json();

            if (data.ok) {
                this.addMessage('STUDIO', data.reply, 'bot');
                
                // Handle navigation/search redirect
                console.log('Full response:', data);
                if (data.navigation && data.navigation.redirect_url) {
                    console.log('Navigation redirect:', data.navigation.redirect_url);
                    setTimeout(() => {
                        const opened = window.open(data.navigation.redirect_url, '_blank');
                        if (!opened) console.log('Popup blocked - navigation');
                    }, 1000);
                } else if (data.search && data.search.redirect_url) {
                    console.log('Search redirect:', data.search.redirect_url);
                    setTimeout(() => {
                        const opened = window.open(data.search.redirect_url, '_blank');
                        if (!opened) {
                            console.log('Popup blocked - trying location.href');
                            window.location.href = data.search.redirect_url;
                        }
                    }, 1000);
                } else if (data.music && data.music.redirect_url) {
                    console.log('Music redirect:', data.music.redirect_url);
                    setTimeout(() => {
                        // Open music player (handles both Spotify and YouTube)
                        window.open(data.music.redirect_url, '_blank');
                    }, 1000);
                } else if (data.shutdown && data.shutdown.action === 'close_window') {
                    console.log('Shutting down STUDIO...');
                    setTimeout(() => {
                        window.close();
                    }, 2000);
                } else {
                    console.log('No redirect found');
                }
                
                // Play TTS if enabled and audio provided
                if (this.ttsEnabled && data.audio_base64) {
                    this.playAudio(data.audio_base64);
                }
            } else {
                this.addMessage('System', data.error || 'Failed to process message', 'bot');
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('System', `Network error: ${error.message}. Make sure Flask server is running on port 5000.`, 'bot');
        }
    }

    addMessage(sender, content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${content}`;
        
        this.messagesPanel.appendChild(messageDiv);
        this.messagesPanel.scrollTop = this.messagesPanel.scrollHeight;
    }

    playAudio(base64Audio) {
        try {
            const audio = new Audio(`data:audio/wav;base64,${base64Audio}`);
            audio.play().catch(error => {
                console.error('Error playing audio:', error);
            });
        } catch (error) {
            console.error('Error creating audio:', error);
        }
    }

    async toggleWakeWord() {
        if (!this.wakeWordActive) {
            await this.startWakeWordListening();
        } else {
            this.stopWakeWordListening();
        }
    }

    async startWakeWordListening() {
        if (!this.microphoneGranted) {
            this.addMessage('System', 'Microphone access required.', 'bot');
            return;
        }

        try {
            this.wakeWordRecorder = new MediaRecorder(this.microphoneStream);
            this.wakeWordChunks = [];

            this.wakeWordRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.wakeWordChunks.push(event.data);
                }
            };

            this.wakeWordRecorder.onstop = () => {
                this.processWakeWordAudio();
            };

            this.wakeWordRecorder.start();
            this.wakeWordActive = true;
            this.wakeWordBtn.textContent = '🔴 Listening for "Studio"';
            this.wakeWordBtn.style.background = '#ff4444';
            this.voiceStatus.textContent = 'Say "Studio" to activate';
            
            this.wakeWordInterval = setInterval(() => {
                if (this.wakeWordRecorder && this.wakeWordRecorder.state === 'recording') {
                    this.wakeWordRecorder.stop();
                    setTimeout(() => {
                        if (this.wakeWordActive) {
                            this.wakeWordRecorder.start();
                        }
                    }, 100);
                }
            }, 2000);

        } catch (error) {
            console.error('Error starting wake word listening:', error);
            this.addMessage('System', 'Wake word detection failed.', 'bot');
        }
    }

    stopWakeWordListening() {
        if (this.wakeWordRecorder && this.wakeWordRecorder.state === 'recording') {
            this.wakeWordRecorder.stop();
        }
        if (this.wakeWordInterval) {
            clearInterval(this.wakeWordInterval);
        }
        this.wakeWordActive = false;
        this.wakeWordBtn.textContent = '🎧 Start Listening';
        this.wakeWordBtn.style.background = '#00ff41';
        this.voiceStatus.textContent = 'Click microphone to speak';
    }

    async processWakeWordAudio() {
        if (!this.wakeWordActive || this.wakeWordChunks.length === 0) return;

        const audioBlob = new Blob(this.wakeWordChunks, { type: 'audio/webm' });
        this.wakeWordChunks = [];

        if (audioBlob.size < 500) return;

        try {
            const formData = new FormData();
            formData.append('audio', audioBlob);

            const response = await fetch('http://127.0.0.1:5000/wake-word', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.wake_word_detected) {
                this.addMessage('System', 'Wake word detected!', 'bot');
                this.voiceStatus.textContent = 'Wake word detected!';
                this.reactorCore.style.animation = 'recordingPulse 0.5s infinite';
                
                setTimeout(() => {
                    this.startCommandRecording();
                }, 200);
            }

        } catch (error) {
            console.error('Wake word error:', error);
        }
    }

    async startCommandRecording() {
        if (!this.microphoneGranted) return;

        try {
            this.stopWakeWordListening();
            
            this.commandRecorder = new MediaRecorder(this.microphoneStream);
            this.commandChunks = [];

            this.commandRecorder.ondataavailable = (event) => {
                this.commandChunks.push(event.data);
            };

            this.commandRecorder.onstop = () => {
                this.processCommandAudio();
                setTimeout(() => {
                    this.startWakeWordListening();
                }, 1000);
            };

            this.commandRecorder.start();
            this.voiceStatus.textContent = 'Listening for command... (3 seconds)';
            
            setTimeout(() => {
                if (this.commandRecorder && this.commandRecorder.state === 'recording') {
                    this.commandRecorder.stop();
                }
            }, 3000);

        } catch (error) {
            console.error('Error starting command recording:', error);
        }
    }

    async processCommandAudio() {
        const audioBlob = new Blob(this.commandChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob);

        try {
            const response = await fetch('http://127.0.0.1:5000/asr', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.ok) {
                this.addMessage('You', data.transcript, 'user');
                this.addMessage('STUDIO', data.reply, 'bot');
                
                // Handle redirects
                if (data.navigation && data.navigation.redirect_url) {
                    setTimeout(() => {
                        window.open(data.navigation.redirect_url, '_blank');
                    }, 1000);
                } else if (data.search && data.search.redirect_url) {
                    setTimeout(() => {
                        window.open(data.search.redirect_url, '_blank');
                    }, 1000);
                } else if (data.shutdown && data.shutdown.action === 'close_window') {
                    setTimeout(() => {
                        window.close();
                    }, 2000);
                } else if (data.music && data.music.redirect_url) {
                    setTimeout(() => {
                        window.open(data.music.redirect_url, '_blank');
                    }, 1000);
                } else if (data.music && data.music.redirect_url) {
                    setTimeout(() => {
                        window.open(data.music.redirect_url, '_blank');
                    }, 1000);
                }
                
                // Play TTS audio
                if (data.audio_base64) {
                    this.playAudio(data.audio_base64);
                }
            } else {
                this.addMessage('System', data.error || 'Failed to process voice command', 'bot');
            }

        } catch (error) {
            console.error('Error processing command:', error);
            this.addMessage('System', 'Error processing voice command', 'bot');
        }

        this.reactorCore.style.animation = '';
        this.voiceStatus.textContent = 'Say "Studio" to activate';
    }
}

// Initialize the assistant when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Check for getUserMedia support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('getUserMedia not supported');
    }
    
    new STUDIOAssistant();
});