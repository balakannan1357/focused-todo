# AI Chess Battle

This repo contains a simple Streamlit application where two language models play chess against each other.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Azure OpenAI credentials and deployments via environment variables:
   ```bash
   export AZURE_OPENAI_API_KEY=your_api_key
   export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   export AZURE_OPENAI_API_VERSION=2024-05-13
   export AGENT1_DEPLOYMENT=gpt-deployment-1
   export AGENT2_DEPLOYMENT=gpt-deployment-2
   ```

3. Launch the Streamlit app:
   ```bash
   streamlit run app.py
   ```

The app alternates moves between two Azure GPT deployments. After the specified number of moves, a simple material evaluation indicates which side has the advantage.
