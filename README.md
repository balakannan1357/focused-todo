# AI Chess Battle

This repo contains a simple Streamlit application where two language models play chess against each other.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your API tokens as environment variables:
   ```bash
   export OPENAI_API_KEY=your_openai_token
   export ANTHROPIC_API_KEY=your_anthropic_token  # optional
   ```

3. Launch the Streamlit app:
   ```bash
   streamlit run app.py
   ```

The app alternates moves between GPT-4o (OpenAI) and Claude (Anthropic). The board is evaluated by a simple material count to show who is ahead.
