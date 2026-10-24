
from __future__ import annotations

import logging
import re
import sqlite3
import httpx

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from google.genai.errors import APIError
from pydantic import BaseModel, Field

from backend.database import (
    initialize_database,
    get_connection,
    DEFAULT_CSV,
    DEFAULT_DB,
)
from backend.analytics import run_analytics
from backend.interpreter import answer_question, _rule_based_interpret

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not DEFAULT_DB.exists():
        initialize_database(DEFAULT_CSV, DEFAULT_DB)
    yield


app = FastAPI(
    title="Mini AI Business Intelligence Assistant",
    version="2.2.0",
    lifespan=lifespan,
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


def classify_question(question: str) -> tuple[str | None, dict]:
    """Map common natural-language questions to supported analytics intents."""
    q = re.sub(r"\s+", " ", question.lower()).strip()

    # Revenue comparison: require explicit month and year for both months.
    month_pattern = (
        r"\b(january|february|march|april|may|june|july|"
        r"august|september|october|november|december)"
        r"\s+(20\d{2})\b"
    )
    months = list(re.finditer(month_pattern, q))

    if (
        re.search(r"\b(compare|comparison|change|changed|difference)\b", q)
        and re.search(r"\brevenue\b", q)
        and len(months) >= 2
    ):
        parsed = []
        for match in months[:2]:
            month = datetime.strptime(match.group(1).title(), "%B")
            parsed.append(f"{match.group(2)}-{month.month:02d}")

        return "revenue_comparison", {
            "month_a": parsed[0],
            "month_b": parsed[1],
        }

    if (
        re.search(r"\b(monthly|month[- ]by[- ]month)\b", q)
        and re.search(r"\b(revenue|sales|trend)\b", q)
    ):
        return "monthly_trend", {}

    if (
        re.search(r"\b(region|territory)\b", q)
        and re.search(r"\b(highest|highest[- ]sales|top|most|best)\b", q)
    ):
        return "top_region", {}

    if (
        re.search(r"\b(product|item)\b", q)
        and re.search(r"\b(highest|highest[- ]revenue|most|top|best)\b", q)
        and re.search(r"\b(revenue|sales|generated)\b", q)
    ):
        return "top_product", {}

    if re.search(r"\b(top[- ]selling|best[- ]selling|most sold|most popular)\b", q):
        return "top_selling_product", {}

    if (
        re.search(r"\b(total|overall|sum)\b", q)
        and re.search(r"\b(revenue|sales)\b", q)
    ):
        return "total_revenue", {}

    if re.search(r"\b(average order value|avg order value)\b", q):
        return "average_order_value", {}

    if (
        re.search(r"\b(total|number of|how many|count)\b", q)
        and re.search(r"\b(units|quantity)\b", q)
    ):
        return "total_units", {}

    if (
        re.search(r"\b(total|number of|how many|count)\b", q)
        and re.search(r"\b(transactions|sales records)\b", q)
    ):
        return "transaction_count", {}

    if (
        re.search(r"\b(total|overall|sum)\b", q)
        and re.search(r"\b(discounts|discount amount)\b", q)
    ):
        return "total_discounts", {}

    return None, {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    conn = None

    try:
        conn = get_connection(DEFAULT_DB)

        intent, params = classify_question(question)

        if intent is not None:
            # Fast path: no external AI call for recognized analytics.
            result = run_analytics(conn, intent, params)
            rows = result["supporting_data"]

            logger.info("Answered using predefined analytics: %s", intent)

            return {
                "question": question,
                "answer": result["answer"],
                "intent": result["intent"],
                "metric": result["metric"],
                "sql": None,
                "columns": list(rows[0].keys()) if rows else [],
                "results": rows,
                "supporting_data": rows,
                "row_count": len(rows),
                **(
                    {"summary": result["summary"]}
                    if "summary" in result else {}
                ),
            }

        # Fallback: AI-generated SQL for unmatched questions.
        logger.info("Using AI fallback for an unmatched question")
        result = answer_question(question, conn)
        rows = result["results"]
        row_count = result["row_count"]

        answer = (
            f"Successfully retrieved {row_count} row(s) from your database."
            if row_count
            else "The query ran successfully, but no matching records were found."
        )

        return {
            "question": question,
            "answer": answer,
            "intent": result.get("intent", "ai_generated"),
            "metric": result.get("metric", "general"),
            "sql": result["sql"],
            "columns": result["columns"],
            "results": rows,
            "supporting_data": rows,
            "row_count": row_count,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except APIError as exc:
        logger.exception("Gemini API request failed")
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI fallback is temporarily unavailable. "
                "Please retry later or use a supported analytics question."
            ),
        ) from exc

    except (httpx.TimeoutException, httpx.NetworkError) as exc:
        logger.warning("AI connection error: %s", type(exc).__name__)
        raise HTTPException(
            status_code=503,
            detail="The AI fallback is temporarily unavailable.",
        ) from exc

    except sqlite3.Error as exc:
        logger.warning("Database query failed: %s", exc)
        raise HTTPException(
            status_code=400,
            detail="The database could not process this question.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error while processing question")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred. Check the backend terminal.",
        ) from exc

    finally:
        if conn is not None:
            conn.close()
