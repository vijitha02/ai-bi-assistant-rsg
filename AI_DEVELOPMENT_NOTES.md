# AI Development Notes

## 1. AI Tools Used

- **ChatGPT:** Used as an AI coding assistant to understand requirements, plan the application architecture, troubleshoot errors, improve code, and prepare test cases and documentation.
- **Google Gemini API:** Integrated into the application as an AI-based fallback for interpreting natural-language business questions that are not handled by the rule-based interpreter.

## 2. How AI Was Used During Development

AI assistance was used throughout the development process to accelerate implementation and debugging.

- **Requirement Analysis:** Broke down the challenge requirements into data management, backend API, analytics, AI integration, frontend, and testing.
- **Application Development:** Used AI assistance to understand and implement components involving FastAPI, Streamlit, SQLite, and Python.
- **Question Interpretation:** Developed rule-based logic for recognizing supported business questions and mapping them to analytical operations.
- **Error Handling:** Investigated errors involving unsupported questions, API responses, and AI service availability.
- **Testing:** Used Pytest to run automated tests and validate analytics functionality.
- **Documentation:** Prepared setup instructions, project documentation, and example business questions.

AI-generated suggestions were reviewed and tested during development rather than being treated as automatically correct.

## 3. Problems Encountered

### Natural-Language Question Interpretation

Some questions were not recognized by the initial rule-based classifier because the wording did not match its expected patterns.

**Resolution:** Reviewed the classification logic and worked toward sharing the rule-based interpreter between the API and analytics workflow to improve consistency.

### AI Service Availability

The Gemini API occasionally returned a `503` service-unavailable response, affecting questions that depended on the AI fallback.

**Resolution:** Investigated the fallback workflow and identified the need for more robust exception handling and reliable rule-based responses for supported questions.

### API Debugging

Some requests returned HTTP `400` errors when the application could not identify a supported analytics question. Request logs were also not always visible in the terminal during debugging.

**Resolution:** Checked the API through the health endpoint and interactive API documentation, reviewed the question-classification flow, and used Uvicorn access logging to help investigate requests.

### Development Environment

Git was not initially recognized in PowerShell, which delayed repository setup.

**Resolution:** Switched to creating and uploading the project through the GitHub website instead of relying on Git commands.

## 4. Testing and Validation

Pytest was used to run the project's automated tests. The test run reported 100% passing.

Testing focused on validating analytics functionality. Additional validation is needed to ensure comprehensive coverage of all five required example questions, invalid questions, missing data, returned transactions, zero quantities, and AI service failures.

## 5. Known Limitations

- The application supports a defined set of analytical questions; unsupported questions may not be answered.
- AI fallback availability depends on the external Gemini service and API configuration.
- Data-quality rules need to be consistently applied to missing prices, invalid records, returned transactions, and zero-quantity records.
- The current test results do not, by themselves, establish that every API endpoint and frontend workflow has been tested.
- Deployment and end-to-end behavior should be verified separately from local execution.

## 6. Improvements With One Additional Day

If given another day, I would focus on the following improvements:

1. **Improve question interpretation:** Support more variations in natural-language questions and provide clearer responses for unsupported requests.
2. **Strengthen reliability:** Add timeouts, retry handling where appropriate, and graceful fallback behavior when the Gemini API is unavailable.
3. **Improve data validation:** Define and test consistent rules for missing, invalid, returned, and zero-quantity records.
4. **Expand automated tests:** Add API-level tests, invalid-question tests, edge cases, and tests for AI service failures.
5. **Improve the user interface:** Display supporting figures, clearer error messages, and useful visualizations.
6. **Verify deployment:** Test the complete application online, including frontend-to-backend communication and environment-variable configuration.

## 7. Key Learnings

This project provided practical experience in building an application that connects natural-language question interpretation with deterministic database analytics. It also highlighted the importance of validating AI-assisted code, handling external service failures, writing automated tests, and ensuring that business answers are supported by actual data.

The main takeaway is that AI can accelerate development, but reliable business intelligence still requires correct calculations, clear validation rules, effective error handling, and thorough testing.
