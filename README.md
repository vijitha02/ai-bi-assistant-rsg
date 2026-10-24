# Mini AI Business Intelligence Assistant

An AI-assisted business intelligence application that enables users to ask questions about sales data in natural language and receive answers backed by database queries.

The project combines rule-based question interpretation, Google Gemini integration, FastAPI, Streamlit, and SQLite to make sales analytics accessible through a simple interface.

## Features

- **Natural Language Queries:** Ask questions about sales data in everyday language.
- **Revenue Analytics:** Calculate total revenue and average order value.
- **Product Analytics:** Identify products generating the highest revenue.
- **Regional Analytics:** Compare sales performance across regions.
- **Monthly Trends:** Analyze monthly revenue and compare performance between months.
- **Additional Metrics:** Retrieve units sold, transaction counts, and discount totals.
- **AI Integration:** Uses Google Gemini as a fallback for question interpretation.
- **REST API:** Processes questions and returns structured analytics results through FastAPI.
- **Interactive Interface:** Submit questions and view results through Streamlit.
- **Automated Testing:** Includes tests for analytics functionality.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| AI Integration | Google Gemini API |
| Data Processing | Pandas |
| Testing | Pytest |
| API Server | Uvicorn |

## Project Structure

```text
ai-bi-assistant-rsg/
├── backend/          # API and analytics logic
├── frontend/         # Streamlit application
├── data/             # Data-related files
├── tests/            # Automated tests
├── sales.db          # SQLite sales database
├── requirements.txt  # Python dependencies
├── .gitignore
└── README.md
```

## How It Works

1. The user enters a business question through the Streamlit interface.
2. The frontend sends the question to the FastAPI backend.
3. The backend identifies the supported analytical intent using rule-based interpretation and AI assistance where applicable.
4. The analytics logic queries the SQLite database to calculate the requested result.
5. The application returns the answer and supporting figures to the user.

Analytical results are calculated from the available sales data rather than relying solely on generated text.

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip
- A Google Gemini API key for AI-assisted interpretation

### 1. Clone the Repository

```bash
git clone https://github.com/vijitha02/ai-bi-assistant-rsg.git
cd ai-bi-assistant-rsg
```

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the API Key

Configure your Gemini API key using the environment-variable method supported by the application.

If the application uses a `.env` file, create one in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your actual key. Never commit `.env` or expose API credentials in source code.

### 5. Start the Backend

From the project root, run:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

When the server is running, access:

- **Health Check:** http://127.0.0.1:8000/health
- **API Documentation:** http://127.0.0.1:8000/docs

### 6. Start the Frontend

Open a second terminal, activate the virtual environment, and run:

```bash
streamlit run frontend/app.py
```

This command assumes the Streamlit entry point is `frontend/app.py`.

## Example Questions

Users can ask questions such as:

- What is the total revenue?
- Which product generated the highest revenue?
- What is the monthly revenue trend?
- Which region generated the highest sales?
- How did revenue change between January and February 2026?
- What is the average order value?
- How many units were sold?
- How much discount was given in total?

Results depend on the implemented analytics and the data available in the database.

## Data Handling

The application uses a SQLite database to store and query sales transactions.

Data quality considerations include:

- Missing or invalid values should be handled before they affect analytical calculations.
- Returned transactions should be treated consistently with the application's revenue rules.
- Zero-quantity records should be handled according to the defined validation logic.

The exact treatment of these records depends on the implementation.

## Running Tests

Run the automated tests from the project root:

```bash
python -m pytest -v
```

The tests help validate the analytics logic and identify unexpected behavior. See the `tests/` directory for the implemented test cases.

## Error Handling and Limitations

- Only supported analytical questions can be answered reliably.
- Questions that cannot be interpreted may return an error or use the AI fallback.
- AI services may be temporarily unavailable or subject to API limits.
- Results depend on the quality and completeness of the stored data.
- The application is a challenge prototype and is not intended as a production-ready business intelligence platform.

## Future Improvements

- Expand the range of supported analytical questions.
- Improve data validation and error handling.
- Add more visualizations and comparative reports.
- Strengthen test coverage for invalid questions and data-quality edge cases.
- Deploy the frontend and backend for online access.

## Project Context

Developed as part of the **AI-Assisted Development Challenge for GET Selection**.
