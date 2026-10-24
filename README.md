# Mini AI Business Intelligence Assistant

An AI-powered business intelligence application that allows users to explore sales data by asking questions in natural language. The application combines rule-based analytics, a FastAPI backend, a Streamlit interface, SQLite, and Google Gemini for question interpretation.

## Features

- **Natural Language Queries** — Ask business questions in everyday language.
- **Sales Analytics** — Retrieve total revenue, average order value, units sold, transaction counts, and total discounts.
- **Product Insights** — Identify top-performing products.
- **Regional Insights** — Analyze sales performance across regions.
- **Trend Analysis** — Explore monthly sales trends and compare revenue across periods.
- **AI-Assisted Interpretation** — Uses Google Gemini as a fallback for supported questions that are not handled by rule-based interpretation.
- **REST API** — Processes analytics requests through FastAPI.
- **Interactive UI** — Provides a Streamlit interface for querying sales data.
- **Automated Tests** — Includes tests for analytics functionality.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| AI Integration | Google Gemini API |
| Data Processing | Pandas |
| Testing | Pytest |
| API Server | Uvicorn |

## Project Structure

```text
ai-bi-assistant-rsg/
├── backend/       # API endpoints and analytics logic
├── frontend/      # Streamlit user interface
├── data/          # Project data files
├── tests/         # Automated tests
├── sales.db       # SQLite sales database
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip
- A Google Gemini API key for AI-assisted question interpretation

### 1. Clone the repository

```bash
git clone https://github.com/vijitha02/ai-bi-assistant-rsg.git
cd ai-bi-assistant-rsg
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the API key

Set your Gemini API key as an environment variable. If your application uses a `.env` file, create it in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Keep `.env` out of version control. Make sure the application loads this variable using the configuration method implemented in the code.

### 5. Start the backend

From the project root, run:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Once the server starts, access:

- **Health check:** `http://127.0.0.1:8000/health`
- **API documentation:** `http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open a second terminal, activate the virtual environment, and run the Streamlit entry-point file located in `frontend/`.

For example, if the file is `app.py`:

```powershell
streamlit run frontend/app.py
```

Replace `app.py` with the actual filename in your repository if it differs.

## Example Questions

Try asking questions such as:

- How much money did we make overall?
- Which product generated the highest revenue?
- Show the month-by-month sales trend.
- Which region performed best in sales?
- Compare revenue between January and February 2026.
- What is the average order value?
- How many units were sold?
- How much discount was given in total?

The answers depend on the available sales data and the analytics implemented in the application.

## Running Tests

From the project root, run:

```bash
python -m pytest -v
```

## Security Notes

- Never commit API keys, passwords, or other secrets.
- Keep `.env`, virtual environments, and Python cache files out of the repository.
- Use only non-sensitive sample data in the published database.

## Future Enhancements

- Expand support for analytical questions.
- Improve AI fallback reliability and error handling.
- Add richer visualizations and reporting.
- Deploy the application for public access.

## Project Context

Developed as part of an **AI-Assisted Development Challenge**.

