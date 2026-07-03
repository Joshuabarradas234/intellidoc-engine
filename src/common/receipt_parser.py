"""
Pure parsing helpers for Amazon Textract AnalyzeExpense responses.

Kept free of any AWS client/network/IO so the extraction logic can be unit
tested deterministically. The Lambda handlers import these functions.
"""
from __future__ import annotations

from typing import Any, Optional


# AnalyzeExpense summary field "Type" values we care about, mapped to our schema.
_SUMMARY_FIELD_MAP = {
    "VENDOR_NAME": "vendor",
    "INVOICE_RECEIPT_DATE": "date",
    "TOTAL": "total",
    "SUBTOTAL": "subtotal",
    "TAX": "tax",
}


def _field_type(field: dict) -> Optional[str]:
    return (field.get("Type") or {}).get("Text")


def _field_value(field: dict) -> Optional[str]:
    value = (field.get("ValueDetection") or {}).get("Text")
    return value.strip() if isinstance(value, str) else value


def parse_money(raw: Any) -> Optional[float]:
    """
    Turn a Textract money string ('$1,234.56', '1.234,56', '£12.00') into a float.
    Returns None if nothing numeric can be recovered.
    """
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    # strip currency symbols / letters / spaces, keep digits, separators, sign
    cleaned = "".join(ch for ch in s if ch.isdigit() or ch in ",.-")
    if not cleaned:
        return None
    # If both separators present, assume the last one is the decimal point.
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        # single comma -> treat as decimal separator
        cleaned = cleaned.replace(",", ".")
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None


def parse_line_items(expense_doc: dict) -> list[dict]:
    """Extract line items (description + price) from an AnalyzeExpense document."""
    items: list[dict] = []
    for group in expense_doc.get("LineItemGroups", []):
        for line_item in group.get("LineItems", []):
            row: dict[str, Any] = {}
            for field in line_item.get("LineItemExpenseFields", []):
                ftype = _field_type(field)
                fval = _field_value(field)
                if ftype == "ITEM":
                    row["description"] = fval
                elif ftype == "PRICE":
                    row["price"] = parse_money(fval)
                elif ftype == "QUANTITY":
                    row["quantity"] = fval
            if row:
                items.append(row)
    return items


def parse_analyze_expense(response: dict) -> dict:
    """
    Convert a Textract AnalyzeExpense response into our receipt schema:
        { vendor, date, total, subtotal, tax, line_items, raw_text }
    Missing fields are simply absent/None rather than raising.
    """
    result: dict[str, Any] = {
        "vendor": None,
        "date": None,
        "total": None,
        "subtotal": None,
        "tax": None,
        "line_items": [],
    }

    text_chunks: list[str] = []

    for doc in response.get("ExpenseDocuments", []):
        for field in doc.get("SummaryFields", []):
            ftype = _field_type(field)
            key = _SUMMARY_FIELD_MAP.get(ftype)
            if not key:
                continue
            value = _field_value(field)
            if key in ("total", "subtotal", "tax"):
                result[key] = parse_money(value)
            else:
                result[key] = value
            if value:
                text_chunks.append(str(value))

        result["line_items"].extend(parse_line_items(doc))
        for item in result["line_items"]:
            if item.get("description"):
                text_chunks.append(str(item["description"]))

    # Full-text blob used for the OpenSearch index.
    result["raw_text"] = " ".join(text_chunks)
    return result


def build_search_document(receipt_id: str, parsed: dict) -> dict:
    """Shape the OpenSearch index document from a parsed receipt."""
    return {
        "receipt_id": receipt_id,
        "vendor": parsed.get("vendor"),
        "date": parsed.get("date"),
        "total": parsed.get("total"),
        "content": parsed.get("raw_text", ""),
    }
