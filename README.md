# Chatbot-Rival
![image](https://github.com/Raytengo/Chatbot-Rival/blob/main/img/Demo.png)

An interactive web application where two AI models converse in a dynamic and customizable environment. The models evolve and respond based on configured personalities, world settings, and AI-specific configurations.

## Features ✨

- **Two AI Models Interacting**:
  - Left and right AI agents with customizable personalities and models.
- **Customizable Conversation Settings**:
  - Adjust rounds, world settings, and AI models for a unique chat experience.
- **Real-time Interaction**:
  - Watch the AI conversation unfold live with real-time updates and adjustable parameters.
- **History Management**:
  - Limit conversation history for each interaction, ensuring concise chats.

## How It Works ⚙️

1. **Frontend**:
   - The user interacts with the AI models via a browser interface that displays messages and allows for easy interaction.
2. **Backend**:
   - Flask serves the chat interface and handles communication between the frontend and AI models, fetching responses in real-time.
3. **AI Models**:
   - You can select between multiple AI models, including `grok-2-latest` and `deepseek-chat`, to drive the conversation.
4. **World Setting**:
   - Customize the world setting for the chat, making the conversation unique for different scenarios.

## Challenges and Solutions 🧩

1. **UI Development Struggles**:
   - Initially, I started with the `v0.dev` framework to build the UI. However, I found that it included many unnecessary files and complex structures that weren’t needed for this project. As a result, I decided to rebuild the entire UI from scratch. This was my first time building a UI like this, so it took some extra effort and time to get it right. But in the end, I learned a lot about structuring front-end code and improving the user experience.

2. **AI Memory and Context**:
   - One major challenge was that the AI agents couldn’t remember what they had said earlier, which meant they couldn’t engage in coherent conversations. To solve this, I implemented a conversation history feature so the AIs could remember and reference past interactions. On top of that, I decided to introduce a world-setting feature, allowing users to adjust the context of the conversation and change the setting at any point. This added a new layer of fun and interactivity to the project.

3. **AI Personality Issues**:
   - In the early stages, due to some incomplete code, the AI models often confused their personalities. For example, the girl AI would sometimes take on the boy’s personality and vice versa. This issue was a bit tricky, but after refactoring and optimizing the code, I was able to ensure that each AI agent correctly followed its designated personality, solving this problem.

4. **Configuration Flexibility**:
   - Finally, I wanted to make the project easy to customize, so I decided to centralize all adjustable parameters in the `config.py` file. This made it much easier for users to tweak things like the number of rounds, the AI models used, and other settings without having to dig through the code. It’s a simple change, but it greatly improves the user experience and makes the app more accessible.

## File Overview 📂

- **`chat.js`**:
  - Handles the frontend logic for managing conversation, making requests, and updating the UI.
- **`style.css`**:
  - Provides the styles for the chat interface, ensuring a visually appealing experience.
- **`config.py`**:
  - Stores global configurations such as default models, available models, chat settings, and server configurations.
- **`model_loader.py`**:
  - Loads the appropriate model and fetches AI-generated responses from the backend.
- **`server.py`**:
  - The Flask server managing routes and interactions between frontend and backend, processing chat requests.
- **`setting.py`**:
  - Contains the personality definitions for the AI agents.
- **`index.html`**:
  - The main HTML page that renders the chat interface in the browser.

## PS

I’ve uploaded a variant of this project where users can directly interact with the AI agents, instead of just observing their conversations. Additionally, it preserves the feature to customize the world setting, allowing more dynamic interactions. You can check it out here: [Chatbot Rival - User Interaction Edition](https://github.com/Raytengo/Chatbot)
