# \# Mini AI Business Intelligence Assistant

# 

# An AI-powered Business Intelligence Assistant that helps users analyze sales data by asking questions in natural language. It combines rule-based analytics, AI-powered question interpretation, and an interactive dashboard to make business insights easier to access.

# 

# \## Features

# 

# \- \*\*Natural Language Queries:\*\* Ask questions about sales data using everyday language.

# \- \*\*Sales Analytics:\*\* Analyze total revenue, average order value, units sold, discounts, and transaction counts.

# \- \*\*Product Analysis:\*\* Identify top-performing and best-selling products.

# \- \*\*Regional Analysis:\*\* Compare sales performance across regions.

# \- \*\*Monthly Trends:\*\* Explore sales trends over time.

# \- \*\*Revenue Comparison:\*\* Compare revenue between different periods.

# \- \*\*Interactive Dashboard:\*\* Use a Streamlit interface to submit questions and view results.

# \- \*\*REST API:\*\* FastAPI backend for processing analytics requests.

# \- \*\*AI Integration:\*\* Uses Gemini as a fallback for interpreting questions that are not recognized by the rule-based system.

# \- \*\*Database Integration:\*\* Uses SQLite to store and retrieve sales data.

# 

# \## Tech Stack

# 

# \- \*\*Language:\*\* Python

# \- \*\*Backend:\*\* FastAPI

# \- \*\*Frontend:\*\* Streamlit

# \- \*\*Database:\*\* SQLite

# \- \*\*AI Integration:\*\* Google Gemini API

# \- \*\*Data Processing:\*\* Pandas

# \- \*\*Testing:\*\* Pytest

# \- \*\*API Server:\*\* Uvicorn

# 

# \## Project Structure

# 

# ```text

# mini-ai-bi-assistant/

# ├── backend/

# │   ├── \_\_init\_\_.py

# │   ├── main.py

# │   ├── analytics.py

# │   └── interpreter.py

# ├── tests/

# │   ├── \_\_init\_\_.py

# │   └── test\_analytics.py

# ├── streamlit\_app.py

# ├── requirements.txt

# ├── .gitignore

# └── README.md

# ```

# 

# \*The structure above is illustrative; adjust the filenames to match the files actually present in your repository.\*

# 

# \## Getting Started

# 

# \### 1. Clone the repository

# 

# ```bash

# git clone https://github.com/YOUR\_USERNAME/mini-ai-bi-assistant.git

# cd mini-ai-bi-assistant

# ```

# 

# Replace `YOUR\_USERNAME` with your GitHub username.

# 

# \### 2. Create a virtual environment

# 

# \*\*Windows:\*\*

# 

# ```powershell

# python -m venv .venv

# .\\.venv\\Scripts\\Activate.ps1

# ```

# 

# \### 3. Install dependencies

# 

# ```bash

# pip install -r requirements.txt

# ```

# 

# \### 4. Configure the Gemini API key

# 

# Create a `.env` file in the project root:

# 

# ```env

# GEMINI\_API\_KEY=your\_actual\_api\_key

# ```

# 

# Replace the placeholder with your own API key. \*\*Do not commit the `.env` file to GitHub.\*\*

# 

# Ensure the application loads the environment variable correctly. If your code uses `python-dotenv`, install it and load the environment variables as required.

# 

# \### 5. Run the FastAPI backend

# 

# From the project root:

# 

# ```bash

# python -m uvicorn backend.main:app --reload --port 8000

# ```

# 

# API health check:

# 

# ```text

# http://127.0.0.1:8000/health

# ```

# 

# Interactive API documentation:

# 

# ```text

# http://127.0.0.1:8000/docs

# ```

# 

# \### 6. Run the Streamlit frontend

# 

# Open a second terminal in the project directory and run:

# 

# ```bash

# streamlit run streamlit\_app.py

# ```

# 

# If your Streamlit entry-point filename is different, replace `streamlit\_app.py` with the actual filename.

# 

# \## Example Questions

# 

# Try asking questions such as:

# 

# \- How much money did we make overall?

# \- Which product generated the highest revenue?

# \- Show the month-by-month sales trend.

# \- Which region performed best in sales?

# \- Compare revenue between January and February 2026.

# \- What is the average order value?

# \- How many units were sold?

# \- How much discount was given in total?

# 

# The results depend on the available data and the analytics supported by the application.

# 

# \## Running Tests

# 

# Run the test suite from the project root:

# 

# ```bash

# python -m pytest -v

# ```

# 

# \## Environment Variables

# 

# | Variable | Purpose |

# |---|---|

# | `GEMINI\_API\_KEY` | API key used for Gemini-based question interpretation |

# 

# Keep credentials and other secrets out of source control.

# 

# \## Future Enhancements

# 

# \- Add more analytical question types.

# \- Improve error handling and AI fallback reliability.

# \- Add richer charts and visualizations.

# \- Support larger datasets and additional data sources.

# \- Deploy the frontend and backend for online access.

# 

# \## Author

# 

# Developed as part of an AI-Assisted Development Challenge.

# 

# \## License

# 

# No license has been specified for this project.



