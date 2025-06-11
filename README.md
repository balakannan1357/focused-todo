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

## Tamil Nadu Election Dashboard

This dashboard explores Tamil Nadu assembly election results from 2006–2021 using the official data published by the Election Commission of India.

First fetch the dataset (requires internet access):

```bash
python fetch_eci_data.py
```

Then launch the dashboard:

```bash
streamlit run election_dashboard.py
```

The scraping script downloads constituency wise results for each election year and stores them in `data/tn_elections.csv` which the dashboard reads.
