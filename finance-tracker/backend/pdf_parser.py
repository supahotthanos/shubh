"""Extract transactions from an Amex PDF statement.

Amex layouts vary by card product, but new charges generally appear as one transaction
per line in the form:

    MM/DD/YY*  MERCHANT NAME  CITY  ST   $1,234.56
    MM/DD      MERCHANT NAME  CITY  ST    1,234.56-     <- credit/refund

This parser extracts text via pdfplumber and applies a regex over each line. Credits
(payments, refunds) are captured with negative amounts so they cancel against charges.
The "period" is detected from the closing-date header; falls back to the most common
month across transactions.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

import pdfplumber

# 01/15/26 or 01/15 (year inferred). Trailing '*' marks a foreign-txn flag on Amex.
DATE_RE = r"(\d{2}/\d{2}(?:/\d{2,4})?)\*?"
# Amount: optional $, thousands separators, optional trailing '-' for credits.
AMOUNT_RE = r"-?\$?\s*([\d,]+\.\d{2})(-?)"
LINE_RE = re.compile(rf"^\s*{DATE_RE}\s+(.+?)\s+{AMOUNT_RE}\s*$")

# Statement closing date / period range, used to derive the YYYY-MM bucket.
PERIOD_RE = re.compile(
    r"closing date\s+(\d{2}/\d{2}/\d{2,4})", re.IGNORECASE
)
PERIOD_RANGE_RE = re.compile(
    r"(\d{2}/\d{2}/\d{2,4})\s*[-–to]+\s*(\d{2}/\d{2}/\d{2,4})", re.IGNORECASE
)

SKIP_KEYWORDS = (
    "previous balance", "payment received", "balance forward", "new balance",
    "minimum payment", "credit limit", "available credit", "total fees",
    "total interest", "page ", "account ending", "membership rewards",
    "summary of account",
)


@dataclass
class ParsedTxn:
    txn_date: date
    merchant: str
    description: str
    amount: float  # positive = charge, negative = credit/payment


@dataclass
class ParsedStatement:
    period: str  # 'YYYY-MM'
    period_start: date | None
    period_end: date | None
    transactions: list[ParsedTxn]
    statement_total: float


def _parse_date(s: str, fallback_year: int | None = None) -> date | None:
    s = s.strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%m/%d"):
        try:
            d = datetime.strptime(s, fmt).date()
            if fmt == "%m/%d" and fallback_year is not None:
                d = d.replace(year=fallback_year)
            return d
        except ValueError:
            continue
    return None


def _extract_text(pdf_bytes: bytes) -> str:
    import io
    pages = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
            pages.append(txt)
    return "\n".join(pages)


def _detect_period(text: str) -> tuple[str, date | None, date | None]:
    end_date = None
    start_date = None

    m = PERIOD_RE.search(text)
    if m:
        end_date = _parse_date(m.group(1))

    m = PERIOD_RANGE_RE.search(text)
    if m:
        start_date = _parse_date(m.group(1))
        end_date = _parse_date(m.group(2)) or end_date

    if end_date:
        return f"{end_date.year:04d}-{end_date.month:02d}", start_date, end_date
    return "", start_date, end_date


def parse_amex_pdf(pdf_bytes: bytes, source_filename: str = "") -> ParsedStatement:
    text = _extract_text(pdf_bytes)
    period, period_start, period_end = _detect_period(text)
    fallback_year = period_end.year if period_end else datetime.utcnow().year

    txns: list[ParsedTxn] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        low = line.lower()
        if any(k in low for k in SKIP_KEYWORDS):
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        date_str, desc, amount_str, neg_suffix = m.groups()
        d = _parse_date(date_str, fallback_year=fallback_year)
        if not d:
            continue
        try:
            amt = float(amount_str.replace(",", ""))
        except ValueError:
            continue
        # Trailing '-' or leading '-' marks credit
        if neg_suffix == "-" or line.lstrip().startswith("-"):
            amt = -amt
        # Crude merchant extraction: keep the whole description; we'll show it as-is
        # but categorize on a normalized version.
        merchant = re.sub(r"\s{2,}", " ", desc).strip()
        txns.append(ParsedTxn(txn_date=d, merchant=merchant, description=desc.strip(), amount=amt))

    # If we couldn't detect period from headers, infer from txn months
    if not period and txns:
        months = Counter(f"{t.txn_date.year:04d}-{t.txn_date.month:02d}" for t in txns)
        period = months.most_common(1)[0][0]

    statement_total = round(sum(t.amount for t in txns if t.amount > 0), 2)
    return ParsedStatement(
        period=period or datetime.utcnow().strftime("%Y-%m"),
        period_start=period_start,
        period_end=period_end,
        transactions=txns,
        statement_total=statement_total,
    )
