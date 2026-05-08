from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import time

from fastapi import Cookie, Depends, FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auth import (
    check_password,
    clear_session_cookie,
    require_auth,
    set_session_cookie,
    verify_token,
)
from categorizer import CATEGORY_ORDER, categorize
from db import get_conn, init_db
from insights import build_report
from pdf_parser import parse_amex_pdf

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Finance Tracker", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


# -------- Schemas --------

class BudgetItem(BaseModel):
    category: str
    monthly_limit: float


class BudgetUpdate(BaseModel):
    budgets: list[BudgetItem]


class TxnEdit(BaseModel):
    category: str


class LoginBody(BaseModel):
    password: str


# -------- Auth endpoints --------

@app.post("/api/login")
def login(body: LoginBody, response: Response) -> dict[str, Any]:
    if not check_password(body.password):
        time.sleep(0.25)  # mild brute-force throttle
        raise HTTPException(status_code=401, detail="Incorrect password")
    set_session_cookie(response)
    return {"ok": True}


@app.post("/api/logout")
def logout(response: Response) -> dict[str, Any]:
    clear_session_cookie(response)
    return {"ok": True}


@app.get("/api/me")
def me(ft_session: str | None = Cookie(default=None)) -> dict[str, Any]:
    return {"authenticated": verify_token(ft_session)}


# -------- Data endpoints (all require auth) --------

@app.post("/api/upload", dependencies=[Depends(require_auth)])
async def upload_statement(file: UploadFile = File(...), period: str | None = None) -> dict[str, Any]:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")
    pdf_bytes = await file.read()

    try:
        parsed = parse_amex_pdf(pdf_bytes, source_filename=file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse PDF: {e}")

    if not parsed.transactions:
        raise HTTPException(
            status_code=422,
            detail="No transactions detected. The Amex layout may be unusual — try a different statement or open an issue.",
        )

    target_period = period or parsed.period

    with get_conn() as conn:
        # Replace any existing statement for this period (re-uploads).
        existing = conn.execute("SELECT id FROM statements WHERE period = ?", (target_period,)).fetchone()
        if existing:
            conn.execute("DELETE FROM statements WHERE id = ?", (existing["id"],))

        cur = conn.execute(
            """
            INSERT INTO statements (period, source_filename, statement_total, detected_period_start, detected_period_end)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                target_period,
                file.filename,
                parsed.statement_total,
                parsed.period_start.isoformat() if parsed.period_start else None,
                parsed.period_end.isoformat() if parsed.period_end else None,
            ),
        )
        statement_id = cur.lastrowid

        for t in parsed.transactions:
            conn.execute(
                """
                INSERT INTO transactions (statement_id, txn_date, merchant, description, amount, category)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (statement_id, t.txn_date.isoformat(), t.merchant, t.description, t.amount, categorize(t.merchant)),
            )

    return {
        "period": target_period,
        "transaction_count": len(parsed.transactions),
        "statement_total": parsed.statement_total,
        "replaced_existing": bool(existing),
    }


@app.get("/api/months", dependencies=[Depends(require_auth)])
def list_months() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT s.period,
                   s.uploaded_at,
                   s.statement_total,
                   COUNT(t.id) AS txn_count
            FROM statements s
            LEFT JOIN transactions t ON t.statement_id = s.id AND t.amount > 0
            GROUP BY s.id
            ORDER BY s.period DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


@app.get("/api/months/{period}", dependencies=[Depends(require_auth)])
def get_month(period: str) -> dict[str, Any]:
    with get_conn() as conn:
        report = build_report(conn, period)
    if not report.get("exists"):
        raise HTTPException(status_code=404, detail=f"No statement uploaded for {period}.")
    return report


@app.get("/api/months/{period}/transactions", dependencies=[Depends(require_auth)])
def list_transactions(period: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT t.id, t.txn_date, t.merchant, t.description, t.amount, t.category
            FROM transactions t
            JOIN statements s ON s.id = t.statement_id
            WHERE s.period = ?
            ORDER BY t.txn_date DESC, t.id DESC
            """,
            (period,),
        ).fetchall()
    return [dict(r) for r in rows]


@app.patch("/api/transactions/{txn_id}", dependencies=[Depends(require_auth)])
def update_transaction(txn_id: int, body: TxnEdit) -> dict[str, Any]:
    if body.category not in CATEGORY_ORDER:
        raise HTTPException(status_code=400, detail=f"Unknown category. Allowed: {CATEGORY_ORDER}")
    with get_conn() as conn:
        cur = conn.execute("UPDATE transactions SET category = ? WHERE id = ?", (body.category, txn_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found.")
    return {"ok": True}


@app.delete("/api/months/{period}", dependencies=[Depends(require_auth)])
def delete_month(period: str) -> dict[str, Any]:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM statements WHERE period = ?", (period,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not found.")
    return {"ok": True}


@app.get("/api/budgets", dependencies=[Depends(require_auth)])
def get_budgets() -> dict[str, Any]:
    with get_conn() as conn:
        rows = conn.execute("SELECT category, monthly_limit FROM budgets").fetchall()
    budgets = {r["category"]: r["monthly_limit"] for r in rows}
    return {"categories": CATEGORY_ORDER, "budgets": budgets}


@app.put("/api/budgets", dependencies=[Depends(require_auth)])
def set_budgets(body: BudgetUpdate) -> dict[str, Any]:
    with get_conn() as conn:
        conn.execute("DELETE FROM budgets")
        for b in body.budgets:
            if b.category not in CATEGORY_ORDER:
                raise HTTPException(status_code=400, detail=f"Unknown category {b.category!r}")
            if b.monthly_limit < 0:
                raise HTTPException(status_code=400, detail="Budget must be >= 0")
            conn.execute(
                "INSERT INTO budgets (category, monthly_limit) VALUES (?, ?)",
                (b.category, b.monthly_limit),
            )
    return {"ok": True}


@app.get("/api/budgets/projection", dependencies=[Depends(require_auth)])
def budget_projection() -> dict[str, Any]:
    """Project next month's spend per category from a 3-month trailing average."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT s.period, t.category, SUM(t.amount) AS total
            FROM transactions t
            JOIN statements s ON s.id = t.statement_id
            WHERE t.amount > 0
            GROUP BY s.period, t.category
            ORDER BY s.period DESC
            """
        ).fetchall()
        budgets = {r["category"]: r["monthly_limit"] for r in conn.execute("SELECT category, monthly_limit FROM budgets")}

    by_cat: dict[str, list[float]] = {}
    periods_seen: list[str] = []
    for r in rows:
        if r["period"] not in periods_seen:
            periods_seen.append(r["period"])
        by_cat.setdefault(r["category"], []).append(r["total"])

    projections = []
    for cat, totals in by_cat.items():
        recent = totals[:3]
        avg = sum(recent) / len(recent) if recent else 0
        projections.append({
            "category": cat,
            "trailing_avg": round(avg, 2),
            "current_budget": round(budgets.get(cat, 0), 2),
            "suggested_budget": round(avg * 1.05, 2),  # 5% buffer
            "months_used": len(recent),
        })
    return {"projections": sorted(projections, key=lambda x: -x["trailing_avg"]), "total_months_tracked": len(periods_seen)}


@app.get("/api/trend", dependencies=[Depends(require_auth)])
def spending_trend() -> dict[str, Any]:
    """Month-over-month totals + per-category trend across all uploaded months."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT s.period, t.category, SUM(t.amount) AS total
            FROM transactions t
            JOIN statements s ON s.id = t.statement_id
            WHERE t.amount > 0
            GROUP BY s.period, t.category
            ORDER BY s.period ASC
            """
        ).fetchall()

    periods: list[str] = []
    by_cat: dict[str, dict[str, float]] = {}
    for r in rows:
        if r["period"] not in periods:
            periods.append(r["period"])
        by_cat.setdefault(r["category"], {})[r["period"]] = round(r["total"], 2)

    series = []
    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        series.append({
            "category": cat,
            "values": [by_cat[cat].get(p, 0.0) for p in periods],
        })
    totals = [round(sum(s["values"][i] for s in series), 2) for i in range(len(periods))]
    return {"periods": periods, "totals": totals, "series": series}


# -------- Frontend hosting --------

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")
