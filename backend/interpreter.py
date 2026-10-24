
"""Interpret natural-language questions for the Mini AI BI Assistant.

The interpreter identifies an analytics intent and extracts parameters.
All calculations are delegated to backend.analytics.run_analytics().
"""

from __future__ import annotations

import json
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
import re
from typing import Any

# Gemini is optional. Standard challenge questions work without an API call.
try:
    from google import genai
except ImportError:
    genai = None


MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

SUPPORTED_INTENTS = {
    "total_revenue",
    "top_product",
    "monthly_trend",
    "top_region",
    "revenue_comparison",
    "total_units",
    "total_discounts",
    "transaction_count",
    "average_order_value",
    "top_selling_product",
}

MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

MONTH_PATTERN = (
    r"\b("
    + "|".join(sorted(MONTHS, key=len, reverse=True))
    + r")\.?\s+((?:19|20)\d{2})\b"
)


def _extract_months(question: str) -> list[str]:
    """Extract month-year values and normalize them to YYYY-MM."""

    normalized: list[str] = []

    # Also support dates already written as YYYY-MM.
    for year, month in re.findall(
        r"\b((?:19|20)\d{2})-(0?[1-9]|1[0-2])\b",
        question,
    ):
        value = f"{year}-{int(month):02d}"
        if value not in normalized:
            normalized.append(value)

    for month_name, year in re.findall(
        MONTH_PATTERN, question, flags=re.IGNORECASE
    ):
        month_number = MONTHS[month_name.lower().rstrip(".")]
        value = f"{year}-{month_number:02d}"

        if value not in normalized:
            normalized.append(value)

    # Preserve the order in which month-year values appear in the question.
    matches = list(
        re.finditer(
            MONTH_PATTERN
            + r"|\b((?:19|20)\d{2})-(0?[1-9]|1[0-2])\b",
            question,
            flags=re.IGNORECASE,
        )
    )

    ordered: list[str] = []
    for match in matches:
        if match.group(1):
            month_name = match.group(1).lower().rstrip(".")
            year = match.group(2)
            value = f"{year}-{MONTHS[month_name]:02d}"
        else:
            year = match.group(3)
            month = match.group(4)
            value = f"{year}-{int(month):02d}"

        if value not in ordered:
            ordered.append(value)

    return ordered if ordered else normalized


def _result(intent: str, params: dict[str, Any] | None = None,
            source: str = "rule_based") -> dict[str, Any]:
    """Return a consistent interpretation object."""

    return {
        "intent": intent,
        "params": params or {},
        "source": source,
    }



def _rule_based_interpret(question: str) -> dict[str, Any] | None:
    """Recognize common phrasings of supported sales analytics questions."""

    q = re.sub(r"\s+", " ", question.lower()).strip()
    months = _extract_months(question)

    # 1. Compare revenue between two specified months.
    comparison_words = re.search(
        r"\b(compare|comparison|difference|change|versus|vs\.?|between|"
        r"compared|better|worse|increased|decreased|growth)\b",
        q,
    )
    revenue_words = re.search(
        r"\b(revenue|sales|income|turnover|earnings|money made)\b", q
    )

    if len(months) >= 2 and comparison_words:
        # Avoid treating unrelated comparisons as revenue comparisons.
        if revenue_words or re.search(
            r"\b(better|worse|growth|increased|decreased)\b", q
        ):
            return _result(
                "revenue_comparison",
                {"month_a": months[0], "month_b": months[1]},
            )

    # 2. Monthly revenue trend.
    if (
        re.search(
            r"\b(monthly|month[- ]by[- ]month|trend|over time|"
            r"each month|per month|monthly breakdown)\b",
            q,
        )
        and re.search(
            r"\b(revenue|sales|income|turnover|earnings|money made)\b", q
        )
    ):
        return _result("monthly_trend")

    # 3. Highest-revenue region.
    has_region = re.search(
        r"\b(region|territory|area|location|zone|state)\b", q
    )
    has_ranking = re.search(
        r"\b(highest|top|most|best|maximum|max|greatest|largest|"
        r"leading|strongest|performed best|performed the best)\b",
        q,
    )

    if has_region and (
        has_ranking
        or re.search(r"\b(performed|contributed|generated)\b", q)
    ) and re.search(
        r"\b(revenue|sales|income|turnover|performance|performing)\b", q
    ):
        return _result("top_region")

    # 4. Top-selling product by quantity.
    if (
        re.search(
            r"\b(best[- ]selling|top[- ]selling|most sold|"
            r"best seller|bestseller|fastest[- ]selling|"
            r"most popular|highest[- ]selling)\b",
            q,
        )
        or (
            re.search(r"\b(product|products|item|items)\b", q)
            and re.search(
                r"\b(most|highest|top|maximum|greatest|largest)\b", q
            )
            and re.search(
                r"\b(units|quantity|sold|selling|purchased|orders)\b", q
            )
        )
    ):
        return _result("top_selling_product")

    # 5. Product generating the highest revenue.
    has_product = re.search(
        r"\b(product|products|item|items|goods)\b", q
    )
    has_revenue = re.search(
        r"\b(revenue|sales|income|turnover|earnings|profit|"
        r"generated|earned|brought in|made us|made the most)\b",
        q,
    )
    has_ranking = re.search(
        r"\b(highest|top|most|best|maximum|max|greatest|largest|"
        r"leading|number one|no\.? 1)\b",
        q,
    )

    if has_product and has_ranking and has_revenue:
        return _result("top_product")

    # Common alternatives such as "Which item earned us the most?"
    if (
        re.search(r"\b(which|what)\b", q)
        and re.search(r"\b(product|item|goods)\b", q)
        and re.search(r"\b(earned|generated|made|brought in)\b", q)
        and re.search(r"\bmost\b", q)
    ):
        return _result("top_product")

    # 6. Average order/transaction value.
    if re.search(
        r"\b(average order value|average transaction value|"
        r"average value per (order|transaction|sale)|"
        r"how much is the average order)\b",
        q,
    ):
        return _result("average_order_value")

    # 7. Total discounts.
    if re.search(r"\b(discount|discounts|price reductions)\b", q) and (
        re.search(r"\b(total|overall|sum|amount|how much|all)\b", q)
    ):
        return _result("total_discounts")

    # 8. Total units sold.
    if (
        re.search(
            r"\b(units|quantity|items sold|number of items|"
            r"products sold|pieces sold)\b",
            q,
        )
        and re.search(r"\b(total|overall|sum|how many|count|number)\b", q)
    ):
        return _result("total_units")

    # 9. Transaction or sales-record count.
    if (
        re.search(
            r"\b(transaction|transactions|sales records|records|"
            r"sales transactions|number of sales|orders)\b",
            q,
        )
        and re.search(r"\b(count|number|how many|total)\b", q)
    ):
        return _result("transaction_count")

    # 10. Total revenue: multiple common phrasings.
    # Total revenue: support different natural-language phrasings.
    if (
        re.search(r"\b(total|overall|sum|combined|entire|aggregate)\b", q)
        and re.search(
            r"\b(revenue|sales|income|turnover|earnings)\b", q
        )
    ):
        return "total_revenue", {}

    if re.search(
        r"\b(how much money|how much did we make|"
        r"how much have we made|money did we make)\b",
        q,
    ):
        return "total_revenue", {}

    if re.search(
        r"\b(how much|how many dollars|how much money)\b", q
    ) and re.search(
        r"\b(make|made|earn|earned|generate|generated|"
        r"bring in|brought in|revenue|sales|income)\b",
        q,
    ):
        return _result("total_revenue")

    if re.search(
        r"\b(revenue|sales|income|turnover|earnings)\b", q
    ) and re.search(
        r"\b(total|overall|in total|altogether)\b", q
    ):
        return _result("total_revenue")

    return None



def _gemini_interpret(question: str) -> dict[str, Any] | None:
    """Optional Gemini fallback for questions not recognized by the rules.

    Gemini chooses only from predefined analytics intents. It does not
    generate SQL or execute database operations.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if genai is None or not api_key:
        return None

    prompt = f"""
You classify questions for a sales business intelligence application.

Choose exactly one intent from this list:
{", ".join(sorted(SUPPORTED_INTENTS))}

Return only a valid JSON object with these keys:
- "intent": one supported intent
- "params": an object

For revenue_comparison, params must contain:
- "month_a": first month in YYYY-MM format
- "month_b": second month in YYYY-MM format

Do not invent dates. If the question does not clearly match a supported
intent, return {{"intent": "unsupported", "params": {{}}}}.

Question: {question}
"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        raw = (response.text or "").strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)
        intent = parsed.get("intent")
        params = parsed.get("params", {})

        if intent not in SUPPORTED_INTENTS or not isinstance(params, dict):
            return None

        if intent == "revenue_comparison":
            month_a = params.get("month_a")
            month_b = params.get("month_b")
            valid_month = re.compile(r"^(?:19|20)\d{2}-(?:0[1-9]|1[0-2])$")

            if (
                not isinstance(month_a, str)
                or not isinstance(month_b, str)
                or not valid_month.fullmatch(month_a)
                or not valid_month.fullmatch(month_b)
            ):
                return None

        return _result(intent, params, source="gemini")

    except Exception:
        # Standard questions remain available even if Gemini is down,
        # the quota is exhausted, or the response is invalid.
        return None


def interpret_question(question: str) -> dict[str, Any]:
    """Interpret a question and return an intent plus its parameters.

    Expected use:
        parsed = interpret_question(question)
        result = run_analytics(conn, parsed["intent"], parsed["params"])
    """

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a question.")

    question = question.strip()

    if len(question) > 2000:
        raise ValueError("The question must be 2000 characters or fewer.")

    # Deterministic rules take priority for reliable challenge examples.
    parsed = _rule_based_interpret(question)
    if parsed is not None:
        return parsed

    # Use AI only when the rule-based interpreter cannot identify the intent.
    parsed = _gemini_interpret(question)
    if parsed is not None:
        return parsed

    raise ValueError(
        "I couldn't identify a supported analytics question. Try asking "
        "about total revenue, the top product, monthly revenue trends, "
        "the highest-revenue region, or comparing two months."
    )
def answer_question(question: str, conn) -> dict[str, Any]:
    """Compatibility wrapper for the existing main.py."""

    from backend.analytics import run_analytics

    parsed = interpret_question(question)

    result = run_analytics(
        conn,
        parsed["intent"],
        parsed.get("params", {}),
    )

    return {
        "question": question,
        "intent": parsed["intent"],
        "metric": parsed["intent"],
        "sql": None,
        "columns": (
            list(result["supporting_data"][0].keys())
            if result.get("supporting_data")
            else []
        ),
        "results": result.get("supporting_data", []),
        "supporting_data": result.get("supporting_data", []),
        "row_count": len(result.get("supporting_data", [])),
        "answer": result.get("answer", "Analysis completed."),
        "summary": result.get("summary"),
    }
