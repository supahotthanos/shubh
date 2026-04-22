"""
Report Generator Service

Generates comprehensive AEO/GEO reports for clients.
Supports PDF, Google Slides integration, and CSV export.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
import json


@dataclass
class ReportSection:
    title: str
    content: Any
    chart_data: Optional[Dict] = None
    recommendations: Optional[List[str]] = None


@dataclass
class GeneratedReport:
    title: str
    client_name: str
    period_start: datetime
    period_end: datetime
    sections: List[ReportSection]
    executive_summary: str
    key_metrics: Dict
    generated_at: datetime
    pdf_bytes: Optional[bytes] = None
    csv_data: Optional[str] = None


class ReportGeneratorService:
    """
    Generate comprehensive AEO/GEO reports.

    Report Sections:
    1. Citation Growth Summary
    2. Platform Performance Breakdown
    3. RRF Score Progress
    4. Content Freshness Status
    5. Campaign Performance
    6. Competitive Positioning
    7. Next Month Priorities
    """

    def __init__(self):
        pass

    async def generate_report(
        self,
        client_id: int,
        period_start: datetime,
        period_end: datetime,
        report_type: str = "monthly",
        client_data: Dict = None,
    ) -> GeneratedReport:
        """
        Generate a comprehensive report for a client.

        Args:
            client_id: Client ID
            period_start: Report period start date
            period_end: Report period end date
            report_type: "weekly", "monthly", "quarterly"
            client_data: Pre-fetched client data (optional)
        """
        # In production, this would fetch data from the database
        # For now, we'll structure the report generation logic

        sections = []

        # Section 1: Citation Growth Summary
        citation_section = self._generate_citation_summary(client_data)
        sections.append(citation_section)

        # Section 2: Platform Performance
        platform_section = self._generate_platform_breakdown(client_data)
        sections.append(platform_section)

        # Section 3: RRF Score Progress
        rrf_section = self._generate_rrf_progress(client_data)
        sections.append(rrf_section)

        # Section 4: Content Freshness
        freshness_section = self._generate_freshness_status(client_data)
        sections.append(freshness_section)

        # Section 5: Campaign Performance
        campaign_section = self._generate_campaign_performance(client_data)
        sections.append(campaign_section)

        # Section 6: Competitive Positioning
        competitive_section = self._generate_competitive_analysis(client_data)
        sections.append(competitive_section)

        # Section 7: Next Month Priorities
        priorities_section = self._generate_priorities(client_data)
        sections.append(priorities_section)

        # Generate executive summary
        executive_summary = self._generate_executive_summary(sections, client_data)

        # Extract key metrics for header
        key_metrics = self._extract_key_metrics(client_data)

        return GeneratedReport(
            title=f"{report_type.title()} AEO Report",
            client_name=client_data.get("client_name", "Client"),
            period_start=period_start,
            period_end=period_end,
            sections=sections,
            executive_summary=executive_summary,
            key_metrics=key_metrics,
            generated_at=datetime.utcnow(),
        )

    def _generate_citation_summary(self, data: Dict) -> ReportSection:
        """Generate citation growth summary section"""
        citations = data.get("citations", {})

        content = {
            "total_citations": citations.get("total", 0),
            "new_citations": citations.get("new_this_period", 0),
            "lost_citations": citations.get("lost_this_period", 0),
            "net_change": citations.get("net_change", 0),
            "growth_rate": citations.get("growth_rate", 0),
            "by_mention_type": citations.get("by_type", {}),
        }

        chart_data = {
            "type": "line",
            "title": "Citation Growth Over Time",
            "data": citations.get("trend_data", []),
        }

        recommendations = []
        if content["net_change"] < 0:
            recommendations.append(
                "Citation count decreased. Review content freshness and competitive activity."
            )
        if content["total_citations"] < 10:
            recommendations.append(
                "Low citation volume. Focus on content marketing campaigns to build visibility."
            )

        return ReportSection(
            title="Citation Growth Summary",
            content=content,
            chart_data=chart_data,
            recommendations=recommendations,
        )

    def _generate_platform_breakdown(self, data: Dict) -> ReportSection:
        """Generate platform performance breakdown"""
        platforms = data.get("platforms", {})

        content = {
            "platforms": [
                {
                    "name": p.get("name"),
                    "citations": p.get("citations", 0),
                    "avg_position": p.get("avg_position"),
                    "stability_score": p.get("stability_score", 0),
                    "trend": p.get("trend", "stable"),
                }
                for p in platforms.get("list", [])
            ],
            "best_performing": platforms.get("best_performing"),
            "needs_attention": platforms.get("needs_attention"),
        }

        chart_data = {
            "type": "bar",
            "title": "Citations by Platform",
            "data": content["platforms"],
        }

        recommendations = []
        if platforms.get("needs_attention"):
            for platform in platforms["needs_attention"]:
                recommendations.append(
                    f"{platform}: Low citation rate. Consider platform-specific optimization."
                )

        return ReportSection(
            title="Platform Performance Breakdown",
            content=content,
            chart_data=chart_data,
            recommendations=recommendations,
        )

    def _generate_rrf_progress(self, data: Dict) -> ReportSection:
        """Generate RRF score progress section"""
        rrf_data = data.get("rrf", {})

        content = {
            "avg_rrf_score": rrf_data.get("avg_score", 0),
            "keywords_meeting_threshold": rrf_data.get("meeting_threshold", 0),
            "total_keywords": rrf_data.get("total_keywords", 0),
            "threshold_rate": rrf_data.get("threshold_rate", 0),
            "top_performing_keywords": rrf_data.get("top_keywords", []),
            "keywords_needing_work": rrf_data.get("needs_improvement", []),
        }

        chart_data = {
            "type": "gauge",
            "title": "RRF Visibility Score",
            "value": content["avg_rrf_score"],
            "threshold": 0.020,
        }

        recommendations = []
        if content["threshold_rate"] < 50:
            recommendations.append(
                "Less than half of keywords meet the RRF threshold. "
                "Focus on multi-presence strategies."
            )
        for kw in content["keywords_needing_work"][:3]:
            recommendations.append(
                f'"{kw.get("keyword")}": Need {kw.get("appearances_needed")} more appearances.'
            )

        return ReportSection(
            title="RRF Score Progress",
            content=content,
            chart_data=chart_data,
            recommendations=recommendations,
        )

    def _generate_freshness_status(self, data: Dict) -> ReportSection:
        """Generate content freshness status section"""
        freshness = data.get("freshness", {})

        content = {
            "overall_grade": freshness.get("overall_grade", "N/A"),
            "avg_freshness_score": freshness.get("avg_score", 0),
            "pages_by_grade": freshness.get("grade_distribution", {}),
            "pages_needing_refresh": freshness.get("needs_refresh", []),
            "recently_refreshed": freshness.get("recently_refreshed", []),
        }

        chart_data = {
            "type": "donut",
            "title": "Content Freshness Distribution",
            "data": content["pages_by_grade"],
        }

        recommendations = []
        critical_pages = [p for p in content["pages_needing_refresh"] if p.get("priority") == "critical"]
        for page in critical_pages[:5]:
            recommendations.append(
                f'Critical: "{page.get("title")}" - {page.get("days_old")} days old. '
                f'Estimated {page.get("position_loss")} position loss.'
            )

        return ReportSection(
            title="Content Freshness Status",
            content=content,
            chart_data=chart_data,
            recommendations=recommendations,
        )

    def _generate_campaign_performance(self, data: Dict) -> ReportSection:
        """Generate campaign performance section"""
        campaigns = data.get("campaigns", {})

        content = {
            "active_campaigns": campaigns.get("active_count", 0),
            "total_assets_deployed": campaigns.get("total_assets", 0),
            "assets_generating_citations": campaigns.get("citing_assets", 0),
            "citation_conversion_rate": campaigns.get("conversion_rate", 0),
            "by_campaign_type": campaigns.get("by_type", {}),
            "top_performing_campaigns": campaigns.get("top_campaigns", []),
        }

        chart_data = {
            "type": "bar",
            "title": "Campaign Performance by Type",
            "data": content["by_campaign_type"],
        }

        recommendations = []
        if content["citation_conversion_rate"] < 30:
            recommendations.append(
                "Low campaign-to-citation conversion rate. "
                "Review content quality and placement strategies."
            )

        return ReportSection(
            title="Campaign Performance",
            content=content,
            chart_data=chart_data,
            recommendations=recommendations,
        )

    def _generate_competitive_analysis(self, data: Dict) -> ReportSection:
        """Generate competitive positioning section"""
        competitive = data.get("competitive", {})

        content = {
            "client_position": competitive.get("client_position", 0),
            "share_of_voice": competitive.get("share_of_voice", 0),
            "competitor_rankings": competitive.get("rankings", []),
            "citation_overlap": competitive.get("overlap_analysis", {}),
            "competitor_activity": competitive.get("recent_activity", []),
        }

        chart_data = {
            "type": "bar",
            "title": "Share of Voice Comparison",
            "data": content["competitor_rankings"],
        }

        recommendations = []
        if content["client_position"] > 3:
            recommendations.append(
                f"Currently ranked #{content['client_position']} among competitors. "
                "Increase content velocity and authority building."
            )

        for activity in content["competitor_activity"][:2]:
            if activity.get("type") == "new_content":
                recommendations.append(
                    f"{activity.get('competitor')}: Published new {activity.get('content_type')}. "
                    "Monitor for citation impact."
                )

        return ReportSection(
            title="Competitive Positioning",
            content=content,
            chart_data=chart_data,
            recommendations=recommendations,
        )

    def _generate_priorities(self, data: Dict) -> ReportSection:
        """Generate next month priorities section"""
        # Aggregate recommendations from all sections and prioritize
        all_recommendations = data.get("all_recommendations", [])

        # Categorize by priority
        critical = [r for r in all_recommendations if r.get("priority") == "critical"]
        high = [r for r in all_recommendations if r.get("priority") == "high"]
        medium = [r for r in all_recommendations if r.get("priority") == "medium"]

        content = {
            "critical_actions": critical[:3],
            "high_priority": high[:5],
            "medium_priority": medium[:5],
            "quick_wins": data.get("quick_wins", []),
        }

        return ReportSection(
            title="Next Month Priorities",
            content=content,
            recommendations=[
                f"[{a.get('priority').upper()}] {a.get('action')}"
                for a in (critical + high)[:7]
            ],
        )

    def _generate_executive_summary(
        self, sections: List[ReportSection], data: Dict
    ) -> str:
        """Generate executive summary paragraph"""
        citations = data.get("citations", {})
        rrf = data.get("rrf", {})
        competitive = data.get("competitive", {})

        total_citations = citations.get("total", 0)
        net_change = citations.get("net_change", 0)
        threshold_rate = rrf.get("threshold_rate", 0)
        position = competitive.get("client_position", 0)

        change_text = "increased" if net_change > 0 else "decreased" if net_change < 0 else "remained stable"

        summary = (
            f"This period, your AI visibility {change_text} with {total_citations} total citations "
            f"({'+' if net_change > 0 else ''}{net_change} net change). "
            f"{threshold_rate}% of tracked keywords meet the RRF visibility threshold. "
            f"You currently rank #{position} among tracked competitors for share of voice. "
        )

        # Add key insight
        if net_change < 0:
            summary += "Focus on content freshness and competitive response this month."
        elif threshold_rate < 50:
            summary += "Prioritize multi-presence strategies to improve RRF scores."
        else:
            summary += "Continue current strategies while exploring new keyword opportunities."

        return summary

    def _extract_key_metrics(self, data: Dict) -> Dict:
        """Extract key metrics for report header"""
        return {
            "total_citations": data.get("citations", {}).get("total", 0),
            "citation_change": data.get("citations", {}).get("net_change", 0),
            "rrf_score": data.get("rrf", {}).get("avg_score", 0),
            "freshness_grade": data.get("freshness", {}).get("overall_grade", "N/A"),
            "competitive_position": data.get("competitive", {}).get("client_position", 0),
            "prompt_coverage": data.get("prompts", {}).get("coverage_rate", 0),
        }

    async def export_to_pdf(self, report: GeneratedReport) -> bytes:
        """Render report as a styled PDF via WeasyPrint + Jinja2."""
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape
            from weasyprint import HTML
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"PDF deps not installed: {exc}")

        import os

        templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"
        )
        env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html"]),
        )
        template = env.get_template("report.html")
        html = template.render(report=report)
        return HTML(string=html).write_pdf()

    def export_to_csv(self, report: GeneratedReport) -> str:
        """Export report data to CSV format"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write header info
        writer.writerow(["AEO Report", report.title])
        writer.writerow(["Client", report.client_name])
        writer.writerow(["Period", f"{report.period_start} to {report.period_end}"])
        writer.writerow([])

        # Write key metrics
        writer.writerow(["Key Metrics"])
        for metric, value in report.key_metrics.items():
            writer.writerow([metric, value])
        writer.writerow([])

        # Write section data
        for section in report.sections:
            writer.writerow([section.title])
            if isinstance(section.content, dict):
                for key, value in section.content.items():
                    if not isinstance(value, (list, dict)):
                        writer.writerow([key, value])
            writer.writerow([])

        return output.getvalue()

    def generate_slides_outline(self, report: GeneratedReport) -> Dict:
        """Generate outline for Google Slides integration"""
        slides = []

        # Title slide
        slides.append({
            "type": "title",
            "title": report.title,
            "subtitle": f"{report.client_name} | {report.period_start.strftime('%B %Y')}",
        })

        # Executive summary slide
        slides.append({
            "type": "text",
            "title": "Executive Summary",
            "content": report.executive_summary,
            "metrics": report.key_metrics,
        })

        # Section slides
        for section in report.sections:
            slide = {
                "type": "section",
                "title": section.title,
                "content": section.content,
            }
            if section.chart_data:
                slide["chart"] = section.chart_data
            if section.recommendations:
                slide["recommendations"] = section.recommendations[:3]
            slides.append(slide)

        return {
            "slides": slides,
            "total_slides": len(slides),
            "template": "aeo_report_template",
        }
