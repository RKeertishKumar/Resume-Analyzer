# Resume-Analyzer
A chatbot that analyzes your resume based on current market trends and creates flashcards with common interview questions for chosen career paths.

## Setup Instructions

To run this program, you need to provide your own Gemini API key. Follow these steps to set it up:

1. **Obtain a Gemini API Key:**
   - Go to the [Google AI for developers website](https://ai.google.dev/gemini-api/docs/api-key) and sign in or create an account if you don't have one.
   - Follow their instructions to generate a new API key.

2. **Create a `.env` File:**
   - In the root directory of the project, create a file named `.env`.

3. **Add Your API Key to the `.env` File:**
   - Open the `.env` file and add the following line, replacing `your_api_key_here` with the API key you obtained:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

4. **Ensure `.env` is Not Tracked by Git:**
   - The `.env` file is listed in the `.gitignore` file to prevent it from being tracked by version control. Make sure the `.gitignore` file includes:
     ```
     .env
     ```

With the above setup, the program will be able to use your Gemini API key to function properly. If you encounter any issues, make sure your API key is correctly added to the `.env` file and that the file is in the root directory of your project.
