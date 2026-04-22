"""Real Google Search Console provider."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from app.providers.base import GSCRow


class RealGSCProvider:
    def __init__(self, credentials_path: Optional[str]) -> None:
        from google.oauth2 import service_account  # noqa: WPS433
        from googleapiclient.discovery import build  # noqa: WPS433

        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        self._service = build("searchconsole", "v1", credentials=creds)

    async def fetch_queries(
        self,
        property_url: str,
        days_back: int = 90,
        row_limit: int = 500,
    ) -> List[GSCRow]:
        end = datetime.utcnow().date()
        start = end - timedelta(days=days_back)
        request = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["query"],
            "rowLimit": row_limit,
        }
        response = (
            self._service.searchanalytics()
            .query(siteUrl=property_url, body=request)
            .execute()
        )
        rows_out: List[GSCRow] = []
        for row in response.get("rows", []):
            rows_out.append(
                GSCRow(
                    query=row["keys"][0],
                    clicks=int(row.get("clicks", 0)),
                    impressions=int(row.get("impressions", 0)),
                    ctr=float(row.get("ctr", 0.0)),
                    position=float(row.get("position", 0.0)),
                )
            )
        return rows_out
