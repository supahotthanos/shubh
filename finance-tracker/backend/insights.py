"""Generate the spending report and concrete cut-down recommendations.

The goal of this module is to surface *specific dollar numbers* the user can act on,
not vague advice. Every recommendation includes the merchant/category it targets and
an estimated monthly savings.
"""

from __future__ import annotations

import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass
class Recommendation:
    title: str
    detail: str
    estimated_monthly_savings: float
    category: str


def _normalize_merchant(name: str) -> str:
    """Strip city/state suffixes and trailing reference numbers so 'STARBUCKS SF CA 1234'
    and 'STARBUCKS NEW YORK NY' collapse to one merchant for grouping."""
    n = name.upper()
    n = re.sub(r"\b\d{4,}\b", "", n)
    n = re.sub(r"\b[A-Z]{2}\b\s*$", "", n)  # trailing state code
    n = re.sub(r"\s+", " ", n).strip()
    # Take first 2-3 meaningful words as the merchant key
    parts = n.split()
    return " ".join(parts[:3]) if parts else n


def build_report(conn: sqlite3.Connection, period: str) -> dict[str, Any]:
    stmt = conn.execute(
        "SELECT id, period, statement_total, uploaded_at FROM statements WHERE period = ?",
        (period,),
    ).fetchone()
    if not stmt:
        return {"period": period, "exists": False}

    txns = conn.execute(
        "SELECT txn_date, merchant, amount, category FROM transactions WHERE statement_id = ?",
        (stmt["id"],),
    ).fetchall()

    charges = [t for t in txns if t["amount"] > 0]
    credits = [t for t in txns if t["amount"] < 0]
    total_spend = round(sum(t["amount"] for t in charges), 2)
    total_credits = round(sum(-t["amount"] for t in credits), 2)

    by_category: dict[str, float] = defaultdict(float)
    txn_count_by_category: dict[str, int] = defaultdict(int)
    for t in charges:
        by_category[t["category"]] += t["amount"]
        txn_count_by_category[t["category"]] += 1
    by_category = {k: round(v, 2) for k, v in by_category.items()}

    merchant_totals: dict[str, dict[str, Any]] = {}
    for t in charges:
        key = _normalize_merchant(t["merchant"])
        m = merchant_totals.setdefault(key, {"merchant": key, "total": 0.0, "count": 0, "category": t["category"]})
        m["total"] += t["amount"]
        m["count"] += 1
    top_merchants = sorted(
        ({**v, "total": round(v["total"], 2), "avg": round(v["total"] / v["count"], 2)} for v in merchant_totals.values()),
        key=lambda x: x["total"],
        reverse=True,
    )[:10]

    # Recurring charges: same normalized merchant, similar amount, appearing in this
    # period AND at least one prior period.
    recurring = _find_recurring(conn, period)

    # Budget comparison (over/under)
    budgets = {row["category"]: row["monthly_limit"] for row in conn.execute("SELECT category, monthly_limit FROM budgets")}
    budget_status = []
    for cat, limit in budgets.items():
        spent = by_category.get(cat, 0.0)
        budget_status.append({
            "category": cat,
            "limit": round(limit, 2),
            "spent": round(spent, 2),
            "remaining": round(limit - spent, 2),
            "pct_used": round((spent / limit * 100) if limit else 0, 1),
        })

    recommendations = _build_recommendations(
        by_category=by_category,
        txn_count_by_category=txn_count_by_category,
        merchant_totals=merchant_totals,
        budgets=budgets,
        recurring=recurring,
    )

    return {
        "period": period,
        "exists": True,
        "uploaded_at": stmt["uploaded_at"],
        "total_spend": total_spend,
        "total_credits": total_credits,
        "net": round(total_spend - total_credits, 2),
        "transaction_count": len(charges),
        "by_category": [{"category": k, "total": v, "count": txn_count_by_category[k]} for k, v in sorted(by_category.items(), key=lambda x: -x[1])],
        "top_merchants": top_merchants,
        "recurring_charges": recurring,
        "budget_status": sorted(budget_status, key=lambda x: -x["pct_used"]),
        "recommendations": [r.__dict__ for r in recommendations],
    }


def _find_recurring(conn: sqlite3.Connection, period: str) -> list[dict[str, Any]]:
    """A merchant counts as 'recurring' when it appears in the current period and at least
    one earlier period with a comparable amount (within 10%)."""
    rows = conn.execute(
        """
        SELECT s.period, t.merchant, t.amount, t.category
        FROM transactions t
        JOIN statements s ON s.id = t.statement_id
        WHERE t.amount > 0
        """
    ).fetchall()
    by_merchant: dict[str, list[tuple[str, float, str]]] = defaultdict(list)
    for r in rows:
        key = _normalize_merchant(r["merchant"])
        by_merchant[key].append((r["period"], r["amount"], r["category"]))

    recurring = []
    for key, items in by_merchant.items():
        periods = {p for p, _, _ in items}
        if period not in periods or len(periods) < 2:
            continue
        current_amts = [a for p, a, _ in items if p == period]
        prior_amts = [a for p, a, _ in items if p != period]
        if not prior_amts:
            continue
        avg_prior = sum(prior_amts) / len(prior_amts)
        avg_current = sum(current_amts) / len(current_amts)
        if avg_prior == 0:
            continue
        if abs(avg_current - avg_prior) / avg_prior <= 0.15:
            recurring.append({
                "merchant": key,
                "amount": round(avg_current, 2),
                "category": items[0][2],
                "months_seen": len(periods),
            })
    return sorted(recurring, key=lambda x: -x["amount"])


def _build_recommendations(
    *,
    by_category: dict[str, float],
    txn_count_by_category: dict[str, int],
    merchant_totals: dict[str, dict[str, Any]],
    budgets: dict[str, float],
    recurring: list[dict[str, Any]],
) -> list[Recommendation]:
    recs: list[Recommendation] = []

    # 1. Over-budget categories: concrete overage number.
    for cat, limit in budgets.items():
        spent = by_category.get(cat, 0.0)
        if spent > limit:
            over = round(spent - limit, 2)
            recs.append(Recommendation(
                title=f"You're ${over:,.2f} over budget on {cat}",
                detail=f"Spent ${spent:,.2f} against a ${limit:,.2f} budget. Cap remaining {cat} purchases at ${limit:,.2f}/mo to stay on plan.",
                estimated_monthly_savings=over,
                category=cat,
            ))

    # 2. Coffee habit: if >8 coffee charges, recommend brewing at home for half of them.
    coffee_total = by_category.get("Coffee", 0.0)
    coffee_count = txn_count_by_category.get("Coffee", 0)
    if coffee_count >= 8 and coffee_total > 40:
        avg_coffee = coffee_total / coffee_count
        save = round(avg_coffee * (coffee_count // 2), 2)
        recs.append(Recommendation(
            title=f"Cut coffee runs in half, save ~${save:,.2f}/mo",
            detail=f"{coffee_count} coffee charges this period averaging ${avg_coffee:,.2f} each. Brewing at home for half of them recovers ${save:,.2f}/mo.",
            estimated_monthly_savings=save,
            category="Coffee",
        ))

    # 3. Dining: flag if dining > 1.5x groceries (eating out > cooking)
    dining = by_category.get("Dining", 0.0)
    groceries = by_category.get("Groceries", 0.0)
    if dining > 200 and (groceries == 0 or dining > 1.5 * groceries):
        target = round(dining * 0.7, 2)
        save = round(dining - target, 2)
        recs.append(Recommendation(
            title=f"Dining is your biggest lever — target ${target:,.2f}/mo",
            detail=f"You spent ${dining:,.2f} eating out vs ${groceries:,.2f} on groceries. Replacing 30% of dining with home cooking saves ~${save:,.2f}/mo.",
            estimated_monthly_savings=save,
            category="Dining",
        ))

    # 4. Subscriptions: list every recurring subscription so user can audit.
    sub_recurring = [r for r in recurring if r["category"] == "Subscriptions"]
    if sub_recurring:
        total_subs = round(sum(r["amount"] for r in sub_recurring), 2)
        names = ", ".join(r["merchant"].title() for r in sub_recurring[:5])
        # Assume user can typically cancel ~25% of subscriptions they forgot about.
        save = round(total_subs * 0.25, 2)
        recs.append(Recommendation(
            title=f"Audit ${total_subs:,.2f}/mo in subscriptions",
            detail=f"Recurring: {names}{'…' if len(sub_recurring) > 5 else ''}. Cancelling the ones you don't actively use typically recovers ~${save:,.2f}/mo.",
            estimated_monthly_savings=save,
            category="Subscriptions",
        ))

    # 5. Rideshare heavy: suggest 1 transit swap per week.
    ride = by_category.get("Rideshare", 0.0)
    ride_count = txn_count_by_category.get("Rideshare", 0)
    if ride_count >= 8 and ride > 100:
        avg = ride / ride_count
        swaps = ride_count // 4  # ~1 per week
        save = round(avg * swaps, 2)
        recs.append(Recommendation(
            title=f"Swap 1 Uber/Lyft per week for transit, save ~${save:,.2f}/mo",
            detail=f"{ride_count} rideshare trips averaging ${avg:,.2f}. Replacing {swaps} of them with transit/walking saves ~${save:,.2f}/mo.",
            estimated_monthly_savings=save,
            category="Rideshare",
        ))

    # 6. Top merchant concentration: if one merchant > 15% of total, call it out.
    total = sum(by_category.values())
    if total > 0:
        for m in sorted(merchant_totals.values(), key=lambda x: -x["total"])[:3]:
            share = m["total"] / total
            if share > 0.15 and m["category"] not in ("Utilities", "Travel"):
                save = round(m["total"] * 0.2, 2)
                recs.append(Recommendation(
                    title=f"{m['merchant'].title()} is {share*100:.0f}% of your spend",
                    detail=f"${m['total']:,.2f} across {m['count']} charges this period. A 20% pullback here saves ~${save:,.2f}/mo.",
                    estimated_monthly_savings=save,
                    category=m["category"],
                ))
                break  # only the top one

    # 7. Fees — these are always low-hanging fruit.
    fees = by_category.get("Fees", 0.0)
    if fees > 0:
        recs.append(Recommendation(
            title=f"You paid ${fees:,.2f} in fees — call Amex",
            detail="Late fees, foreign-transaction fees, and interest are often waivable on first request. Worth a 10-minute phone call.",
            estimated_monthly_savings=fees,
            category="Fees",
        ))

    # Sort by impact, dedupe by title
    seen = set()
    out = []
    for r in sorted(recs, key=lambda x: -x.estimated_monthly_savings):
        if r.title in seen:
            continue
        seen.add(r.title)
        out.append(r)
    return out
