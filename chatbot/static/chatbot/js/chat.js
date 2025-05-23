// Chat functionality for the Django chatbot
class ChatBot {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.messagesContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatForm = document.getElementById('chat-form');
        this.typingIndicator = document.getElementById('typing-indicator');

        this.initializeEventListeners();
        this.loadChatHistory();
    }

    generateSessionId() {
        return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Enter key to send message
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Quick question buttons
        document.querySelectorAll('.quick-question').forEach(button => {
            button.addEventListener('click', () => {
                const question = button.getAttribute('data-question');
                this.messageInput.value = question;
                this.sendMessage();
            });
        });

        // Auto-resize input
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Disable input and show loading
        this.setInputState(false);
        this.addUserMessage(message);
        this.messageInput.value = '';
        this.showTypingIndicator();

        try {
            const response = await this.callChatAPI(message);
            this.hideTypingIndicator();

            if (response.success) {
                this.addBotMessage(response.response, response.confidence, response.source);
                this.sessionId = response.session_id; // Update session ID
            } else {
                this.addErrorMessage(response.error || 'حدث خطأ في الاتصال - Connection error');
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('Chat error:', error);
            this.addErrorMessage('حدث خطأ في الاتصال - Connection error');
        } finally {
            this.setInputState(true);
            this.messageInput.focus();
        }
    }

    async callChatAPI(message) {
        const response = await fetch('/chatbot/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });

        return await response.json();
    }

    addUserMessage(message) {
        const messageElement = this.createMessageElement(message, 'user');
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    addBotMessage(message, confidence = null, source = null) {
        const messageElement = this.createMessageElement(message, 'bot', confidence, source);
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    addErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message chat-message';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle mr-2"></i>
            ${message}
        `;
        this.messagesContainer.appendChild(errorDiv);
        this.scrollToBottom();
    }

    createMessageElement(message, type, confidence = null, source = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message flex items-start space-x-4 mb-6 animate-slide-up';

        const isUser = type === 'user';
        const isArabic = this.detectArabic(message);
        const textDirection = isArabic ? 'rtl' : 'ltr';

        if (isUser) {
            messageDiv.className += ' flex-row-reverse space-x-reverse';
        }

        const avatar = document.createElement('div');
        avatar.className = 'relative';
        avatar.innerHTML = `
            <div class="${isUser ? 'bg-gradient-to-br from-purple-500 to-pink-600' : 'bg-gradient-to-br from-blue-500 to-purple-600'} text-white p-3 rounded-2xl shadow-lg transform hover:scale-110 transition-all duration-300">
                <i class="fas ${isUser ? 'fa-user' : 'fa-robot'} text-lg"></i>
            </div>
            ${!isUser ? '<div class="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>' : ''}
        `;

        const messageContent = document.createElement('div');
        messageContent.className = `${isUser ? 'user-message' : 'bot-message'} p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1`;

        let confidenceIndicator = '';
        if (confidence !== null && !isUser) {
            const confidenceClass = confidence > 0.8 ? 'confidence-high' :
                                  confidence > 0.5 ? 'confidence-medium' : 'confidence-low';
            confidenceIndicator = `<span class="confidence-indicator ${confidenceClass}" title="Confidence: ${Math.round(confidence * 100)}%"></span>`;
        }

        let sourceIndicator = '';
        if (source && !isUser) {
            const sourceText = source === 'knowledge_base' ? 'KB' :
                             source === 'database_kb' ? 'DB' : 'AI';
            sourceIndicator = `<span class="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded ml-2" title="Source: ${source}">${sourceText}</span>`;
        }

        messageContent.innerHTML = `
            <div class="${textDirection}">
                <p class="text-gray-800 ${isUser ? 'text-white' : ''} leading-relaxed">${this.formatMessage(message)}</p>
                <div class="flex items-center justify-between mt-4 pt-3 border-t ${isUser ? 'border-white/20' : 'border-gray-100'}">
                    <span class="text-xs ${isUser ? 'text-white/80' : 'text-gray-500'}">
                        ${new Date().toLocaleTimeString()}
                        ${confidenceIndicator}
                        ${sourceIndicator}
                    </span>
                    <div class="flex items-center space-x-1">
                        <div class="w-1 h-1 ${isUser ? 'bg-white/60' : 'bg-green-400'} rounded-full"></div>
                        <span class="text-xs ${isUser ? 'text-white/80' : 'text-green-600'}">${isUser ? 'You' : 'AI Assistant'}</span>
                    </div>
                </div>
                ${!isUser ? this.createFeedbackButtons() : ''}
            </div>
        `;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        return messageDiv;
    }

    createFeedbackButtons() {
        return `
            <div class="feedback-buttons">
                <button class="feedback-btn" onclick="this.sendFeedback('helpful', this)" title="Helpful">
                    <i class="fas fa-thumbs-up"></i>
                </button>
                <button class="feedback-btn" onclick="this.sendFeedback('not_helpful', this)" title="Not helpful">
                    <i class="fas fa-thumbs-down"></i>
                </button>
            </div>
        `;
    }

    async sendFeedback(feedback, button) {
        try {
            const response = await fetch('/chatbot/api/feedback/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message_id: Date.now(), // In real implementation, use actual message ID
                    feedback: feedback
                })
            });

            if (response.ok) {
                // Mark button as active
                button.classList.add('active');
                // Disable other feedback buttons in the same group
                const feedbackButtons = button.parentElement.querySelectorAll('.feedback-btn');
                feedbackButtons.forEach(btn => {
                    if (btn !== button) {
                        btn.disabled = true;
                        btn.style.opacity = '0.5';
                    }
                });
            }
        } catch (error) {
            console.error('Feedback error:', error);
        }
    }

    formatMessage(message) {
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        message = message.replace(urlRegex, '<a href="$1" target="_blank" class="text-blue-500 underline">$1</a>');

        // Convert line breaks to <br>
        message = message.replace(/\n/g, '<br>');

        return message;
    }

    detectArabic(text) {
        const arabicRegex = /[\u0600-\u06FF]/;
        return arabicRegex.test(text);
    }

    showTypingIndicator() {
        this.typingIndicator.classList.remove('hidden');
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.classList.add('hidden');
    }

    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;

        if (enabled) {
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        } else {
            this.sendButton.innerHTML = '<div class="loading-spinner"></div>';
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    loadChatHistory() {
        // In a real implementation, you might want to load previous messages
        // from the server for authenticated users
        console.log('Chat initialized with session ID:', this.sessionId);
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatBot = new ChatBot();

    // Global function for feedback (needed for onclick handlers)
    window.sendFeedback = (feedback, button) => {
        window.chatBot.sendFeedback(feedback, button);
    };
});

// Add some utility functions
window.chatUtils = {
    // Function to embed chat widget in other pages
    embedChatWidget: function(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            fetch('/chatbot/widget/')
                .then(response => response.text())
                .then(html => {
                    container.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error loading chat widget:', error);
                });
        }
    }
};
