<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT-like UI (Streaming)</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        .typing-indicator::after {
            content: '▋';
            animation: blink 1s step-start infinite;
        }
        @keyframes blink {
            50% { opacity: 0; }
        }
        .code-block {
            position: relative;
        }
        .copy-button {
            position: absolute;
            top: 5px;
            right: 5px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 5px 10px;
            font-size: 12px;
            cursor: pointer;
        }
        .copy-button:hover {
            background-color: #45a049;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background-color: #f0f0f0;
        }
        #chat-container {
            flex-grow: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        .message {
            max-width: 70%;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 10px;
        }
        .user-message {
            align-self: flex-end;
            background-color: #dcf8c6;
        }
        .assistant-message {
            align-self: flex-start;
            background-color: #ffffff;
        }
        #input-container {
            display: flex;
            padding: 20px;
            background-color: #ffffff;
        }
        #user-input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        #send-button {
            margin-left: 10px;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div id="chat-container"></div>
    <div id="input-container">
        <input type="text" id="user-input" placeholder="Type your message here...">
        <button id="send-button">Send</button>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');

        function addCopyButtons(messageDiv) {
            const codeBlocks = messageDiv.querySelectorAll('pre code');
            codeBlocks.forEach((codeBlock, index) => {
                const wrapper = document.createElement('div');
                wrapper.className = 'code-block';
                codeBlock.parentNode.insertBefore(wrapper, codeBlock);
                wrapper.appendChild(codeBlock);

                const copyButton = document.createElement('button');
                copyButton.textContent = 'Copy';
                copyButton.className = 'copy-button';
                copyButton.addEventListener('click', () => {
                    navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                        copyButton.textContent = 'Copied!';
                        setTimeout(() => {
                            copyButton.textContent = 'Copy';
                        }, 2000);
                    });
                });
                wrapper.insertBefore(copyButton, codeBlock);
            });
        }

        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(isUser ? 'user-message' : 'assistant-message');
            messageDiv.innerHTML = isUser ? content : '';
            if (!isUser) {
                messageDiv.classList.add('typing-indicator');
            }
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return messageDiv;
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (message) {
                addMessage(message, true);
                userInput.value = '';

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message }),
                    });

                    if (response.ok) {
                        const reader = response.body.getReader();
                        const decoder = new TextDecoder();
                        let assistantMessage = addMessage('', false);
                        let fullResponse = '';

                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) break;
                            
                            const chunk = decoder.decode(value, { stream: true });
                            fullResponse += chunk;
                            assistantMessage.innerHTML = marked.parse(fullResponse);
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }

                        assistantMessage.classList.remove('typing-indicator');
                        addCopyButtons(assistantMessage);
                    } else {
                        addMessage('Error: Failed to get a response from the server.', false);
                    }
                } catch (error) {
                    addMessage('Error: An error occurred while sending the message.', false);
                }
            }
        }

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>




from flask import Flask, render_template, request, Response, stream_with_context
from openai import OpenAI
import traceback

client = OpenAI(api_key='az-v4OWLD2ir3d0hiYCqP1UzqEKmkCcvlSbC7qdnqzshCT3BlbkFJEbX2Q2tMQnDddFRdrsOyoCbjwOzynB4sNBelymyaYA')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('gptui.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # Wrap the user's message in markdown code blocks
    markdown_message = f"```markdown\n{user_message}\n```"
    
    def generate():
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": markdown_message}
                ],
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_message)  # This will print the error in your console
            yield f"Error: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
