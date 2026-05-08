"""Merchant -> category classifier.

Rule-based: keyword/regex match on the merchant string. Order matters — first match wins.
Categories are intentionally broad enough to drive useful insights but narrow enough
to surface specific cuts (e.g. 'Coffee' is split out from 'Dining').
"""

from __future__ import annotations

import re

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Coffee", [
        r"starbucks", r"blue bottle", r"philz", r"peet'?s", r"dunkin", r"caribou",
        r"\bcafe\b", r"coffee", r"la colombe", r"intelligentsia",
    ]),
    ("Groceries", [
        r"whole foods", r"trader joe", r"safeway", r"kroger", r"wegmans", r"publix",
        r"costco", r"sam'?s club", r"aldi", r"sprouts", r"\bh-?e-?b\b", r"ralphs",
        r"food lion", r"giant", r"stop ?& ?shop", r"shoprite", r"erewhon",
    ]),
    ("Dining", [
        r"chipotle", r"sweetgreen", r"shake shack", r"mcdonald", r"chick-?fil-?a",
        r"dominos", r"pizza", r"sushi", r"thai", r"taco bell", r"wendy", r"burger",
        r"restaurant", r"grill", r"kitchen", r"bistro", r"bar ?& ?", r"\bbbq\b",
        r"deli", r"diner", r"steakhouse", r"ramen", r"pho ", r"\bdoordash\b",
        r"\bgrubhub\b", r"\buber ?eats\b", r"caviar", r"seamless", r"postmates",
    ]),
    ("Groceries", [r"\bmarket\b", r"\bmart\b"]),  # generic fallback after named chains
    ("Rideshare", [r"\buber\b(?! ?eats)", r"\blyft\b", r"\bcurb\b", r"\bvia\b"]),
    ("Gas", [r"shell", r"chevron", r"exxon", r"mobil", r"bp ", r"sunoco", r"\b76\b", r"arco"]),
    ("Transit", [r"\bmta\b", r"\bbart\b", r"\bcaltrain\b", r"\bsfmta\b", r"\bclipper\b", r"metro", r"transit"]),
    ("Travel", [
        r"airline", r"airways", r"\bdelta\b", r"united", r"american air", r"southwest",
        r"jetblue", r"alaska air", r"\bspirit\b", r"frontier", r"hotel", r"marriott",
        r"hilton", r"hyatt", r"airbnb", r"vrbo", r"expedia", r"booking\.com", r"kayak",
        r"\btsa\b", r"clear ", r"global entry",
    ]),
    ("Subscriptions", [
        r"netflix", r"spotify", r"hulu", r"disney\+?", r"hbo", r"max\.com", r"apple\.com/bill",
        r"icloud", r"google\s*\*?storage", r"dropbox", r"adobe", r"github", r"openai",
        r"anthropic", r"chatgpt", r"\bchegg\b", r"\bmedium\b", r"new york times",
        r"\bnyt\b", r"wsj", r"washington post", r"patreon", r"substack", r"\bnotion\b",
        r"figma", r"\bcanva\b", r"\blinkedin\b", r"audible", r"youtube premium", r"paramount\+",
        r"peacock", r"\bduolingo\b", r"\bgrammarly\b", r"1password", r"lastpass",
    ]),
    ("Utilities", [r"comcast", r"xfinity", r"verizon", r"\bat&t\b", r"\bt-?mobile\b", r"sprint", r"pg&e", r"con ?ed", r"electric", r"\bgas co\b", r"water", r"sewer"]),
    ("Health", [r"pharmacy", r"cvs", r"walgreens", r"rite aid", r"hospital", r"clinic", r"dental", r"vision", r"\bgym\b", r"equinox", r"planet fitness", r"peloton", r"barry'?s", r"soulcycle", r"\byoga\b", r"\bpilates\b"]),
    ("Shopping", [r"amazon", r"\bamzn\b", r"target", r"walmart", r"best buy", r"apple store", r"\bnike\b", r"adidas", r"\bzara\b", r"\buniqlo\b", r"\bh&m\b", r"sephora", r"ulta", r"\bikea\b", r"\betsy\b", r"\bebay\b"]),
    ("Entertainment", [r"\bamc\b", r"regal", r"cinema", r"theatre", r"theater", r"ticketmaster", r"stubhub", r"\bsteam\b", r"playstation", r"xbox", r"nintendo"]),
    ("Fees", [r"interest charge", r"late fee", r"foreign transaction", r"annual fee", r"\bfee\b"]),
]

CATEGORY_ORDER = [
    "Groceries", "Dining", "Coffee", "Rideshare", "Gas", "Transit", "Travel",
    "Subscriptions", "Utilities", "Health", "Shopping", "Entertainment", "Fees", "Other",
]


def categorize(merchant: str) -> str:
    text = (merchant or "").lower()
    for category, patterns in CATEGORY_RULES:
        for pat in patterns:
            if re.search(pat, text):
                return category
    return "Other"
