# AI Future Self Simulator

An AI agent that helps you think through big life decisions like career moves, grad school, starting a business, etc. by simulating how each choice could play out over time.

You describe a decision and some personal context. The agent researches current data (job markets, cost of living, etc.), generates distinct paths, analyzes pros/cons, projects future timelines, compares trade-offs, and distills a key insight. Results stream to your browser in real time.

## Example

**Input:**

```json
{
  "decision": "Should I accept the MS program or start a consultancy?",
  "context": "Age 28, software engineer, $120k salary, $40k savings, $15k student loans, partner works remotely",
  "num_choices": 3,
  "time_horizons": ["6 months", "1 year", "3 years"]
}
```

**Output** (streamed via SSE):
- 3 (modifiable) distinct pathways with detailed pros/cons
- Vivid timeline projections at each horizon
- Pairwise trade-off comparisons
- A synthesized key insight and reflective question
- Downloadable PDF report

## Setup

### Prerequisites

- Python 3.11+
- An Azure OpenAI resource with a deployed model (e.g. `gpt-4o`)

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/future-self-simulator.git
cd future-self-simulator
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Copy the template and fill in your Azure OpenAI values:

```bash
cp .env.example .env
```

Edit `.env`:

```
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

Find these in **Azure Portal → your OpenAI resource → Keys and Endpoint**.

### 3. Run

```bash
python app.py
```

Open **http://localhost:8000** in your browser.

### 4. Verify

Health check:

```bash
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok","azure_openai_configured":true}`

## Running with Docker (optional)

```bash
docker-compose up --build
```

App runs at **http://localhost:8000**.

## Deploy to Azure (optional)

A full deployment script is included at `.azure/deploy.example.ps1`. Copy it to `.azure/deploy.ps1`, fill in your subscription ID and resource names, then run:

```powershell
.\.azure\deploy.ps1 -SubscriptionId "your-subscription-id" -Location "eastus"
```

This creates: Container Registry, Container App, Key Vault, Application Insights, and a public HTTPS endpoint.

## Demo Mode

If no Azure OpenAI credentials are configured, the app automatically runs in demo mode with simulated responses — useful for testing the UI.

## Project Structure

```
├── app.py                 # FastAPI server
├── agent.py               # 6-step agentic reasoning pipeline
├── llm_client.py          # Azure OpenAI client
├── research_tools.py      # Web research (DuckDuckGo, no API key needed)
├── prompts.py             # Structured prompt templates
├── models.py              # Pydantic data models
├── config.py              # Environment configuration
├── demo_mode.py           # Simulated responses for demo mode
├── static/index.html      # Single-page frontend
├── Dockerfile             # Container build
├── docker-compose.yml     # Local Docker setup
├── .env.example           # Credential template (copy to .env)
└── .azure/
    └── deploy.example.ps1 # Azure deployment script template
```

## License

MIT
