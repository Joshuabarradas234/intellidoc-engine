"""Unit tests for the Textract AnalyzeExpense parser (pure logic)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "common"))

from receipt_parser import (  # noqa: E402
    build_search_document,
    parse_analyze_expense,
    parse_line_items,
    parse_money,
)


# ── parse_money ───────────────────────────────────────────────────────────────

def test_parse_money_plain():
    assert parse_money("12.50") == 12.50

def test_parse_money_with_currency_symbol():
    assert parse_money("$1,234.56") == 1234.56
    assert parse_money("£12.00") == 12.00

def test_parse_money_european_format():
    assert parse_money("1.234,56") == 1234.56

def test_parse_money_comma_decimal():
    assert parse_money("12,50") == 12.50

def test_parse_money_none_and_garbage():
    assert parse_money(None) is None
    assert parse_money("N/A") is None

def test_parse_money_passthrough_number():
    assert parse_money(9.99) == 9.99


# ── parse_analyze_expense ─────────────────────────────────────────────────────

def _summary(field_type, text):
    return {"Type": {"Text": field_type}, "ValueDetection": {"Text": text}}

def test_parse_expense_summary_fields():
    response = {
        "ExpenseDocuments": [
            {
                "SummaryFields": [
                    _summary("VENDOR_NAME", "Blue Bottle Coffee"),
                    _summary("INVOICE_RECEIPT_DATE", "2026-05-01"),
                    _summary("TOTAL", "$14.20"),
                    _summary("TAX", "$1.20"),
                ],
                "LineItemGroups": [],
            }
        ]
    }
    parsed = parse_analyze_expense(response)
    assert parsed["vendor"] == "Blue Bottle Coffee"
    assert parsed["date"] == "2026-05-01"
    assert parsed["total"] == 14.20
    assert parsed["tax"] == 1.20
    assert "Blue Bottle Coffee" in parsed["raw_text"]

def test_parse_expense_missing_fields_are_none():
    parsed = parse_analyze_expense({"ExpenseDocuments": [{"SummaryFields": []}]})
    assert parsed["vendor"] is None
    assert parsed["total"] is None
    assert parsed["line_items"] == []

def test_parse_expense_empty_response():
    parsed = parse_analyze_expense({})
    assert parsed["vendor"] is None
    assert parsed["raw_text"] == ""


# ── parse_line_items ──────────────────────────────────────────────────────────

def test_parse_line_items():
    doc = {
        "LineItemGroups": [
            {
                "LineItems": [
                    {
                        "LineItemExpenseFields": [
                            {"Type": {"Text": "ITEM"}, "ValueDetection": {"Text": "Latte"}},
                            {"Type": {"Text": "PRICE"}, "ValueDetection": {"Text": "4.50"}},
                        ]
                    }
                ]
            }
        ]
    }
    items = parse_line_items(doc)
    assert items == [{"description": "Latte", "price": 4.50}]


# ── build_search_document ─────────────────────────────────────────────────────

def test_build_search_document():
    parsed = {"vendor": "ACME", "date": "2026-01-01", "total": 10.0, "raw_text": "ACME widget"}
    doc = build_search_document("abc-123", parsed)
    assert doc["receipt_id"] == "abc-123"
    assert doc["vendor"] == "ACME"
    assert doc["content"] == "ACME widget"
