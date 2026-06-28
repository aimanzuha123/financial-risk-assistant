"""
PDF Report Generator
Generates executive business reports as PDF documents using reportlab.
"""
import io
from datetime import datetime
from typing import Dict, List, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image
)
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie


class PDFReportGenerator:
    """Generates professional PDF executive reports."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles for the report."""
        self.styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=self.styles["Title"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=30,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            parent=self.styles["Heading1"],
            fontSize=16,
            textColor=colors.HexColor("#16213e"),
            spaceBefore=20,
            spaceAfter=10,
            borderWidth=1,
            borderColor=colors.HexColor("#0f3460"),
            borderPadding=5,
        ))
        self.styles.add(ParagraphStyle(
            name="SubHeader",
            parent=self.styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#0f3460"),
            spaceBefore=12,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name="BodyText2",
            parent=self.styles["BodyText"],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14,
        ))
        self.styles.add(ParagraphStyle(
            name="MetricLabel",
            parent=self.styles["BodyText"],
            fontSize=9,
            textColor=colors.HexColor("#666666"),
        ))
        self.styles.add(ParagraphStyle(
            name="MetricValue",
            parent=self.styles["BodyText"],
            fontSize=14,
            textColor=colors.HexColor("#1a1a2e"),
            fontName="Helvetica-Bold",
        ))

    def generate_report(self, report_data: Dict[str, Any], output_path: str) -> str:
        """
        Generate a complete executive PDF report.

        Args:
            report_data: Dictionary containing all report sections.
            output_path: File path to save the PDF.

        Returns:
            The file path of the generated PDF.
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=60,
            leftMargin=60,
            topMargin=50,
            bottomMargin=50,
        )

        story = []

        # Title Page
        story.extend(self._build_title_page(report_data))
        story.append(PageBreak())

        # Executive Summary
        if "executive_summary" in report_data:
            story.extend(self._build_section(
                "Executive Summary", report_data["executive_summary"]
            ))

        # Business Insights
        if "business_insights" in report_data:
            story.extend(self._build_section(
                "Business Insights", report_data["business_insights"]
            ))

        # Risk Trends
        if "risk_trends" in report_data:
            story.extend(self._build_risk_section(report_data["risk_trends"]))

        # Customer Segmentation
        if "customer_segmentation" in report_data:
            story.extend(self._build_table_section(
                "Customer Segmentation", report_data["customer_segmentation"]
            ))

        story.append(PageBreak())

        # Recommendations
        if "recommendations" in report_data:
            story.extend(self._build_list_section(
                "Recommendations", report_data["recommendations"]
            ))

        # Financial Impact
        if "financial_impact" in report_data:
            story.extend(self._build_section(
                "Financial Impact Analysis", report_data["financial_impact"]
            ))

        # Intervention Strategy
        if "intervention_strategy" in report_data:
            story.extend(self._build_list_section(
                "Intervention Strategy", report_data["intervention_strategy"]
            ))

        # Next Steps
        if "next_steps" in report_data:
            story.extend(self._build_list_section(
                "Next Steps", report_data["next_steps"]
            ))

        # Model Performance
        if "model_performance" in report_data:
            story.extend(self._build_model_section(report_data["model_performance"]))

        # Footer
        story.extend(self._build_footer())

        doc.build(story)
        return output_path

    def _build_title_page(self, data: Dict) -> List:
        """Build the title page."""
        elements = []
        elements.append(Spacer(1, 100))

        # Decorative line
        elements.append(HRFlowable(
            width="80%", thickness=3,
            color=colors.HexColor("#0f3460"),
            spaceAfter=20,
        ))

        elements.append(Paragraph(
            "Executive Business Report",
            self.styles["ReportTitle"],
        ))

        elements.append(Paragraph(
            "AI-Powered Financial Risk & Collections Analysis",
            self.styles["SubHeader"],
        ))

        elements.append(HRFlowable(
            width="80%", thickness=1,
            color=colors.HexColor("#0f3460"),
            spaceBefore=20, spaceAfter=40,
        ))

        # Metadata table
        meta = [
            ["Report Date", datetime.now().strftime("%B %d, %Y")],
            ["Dataset", data.get("dataset_name", "N/A")],
            ["Records Analyzed", str(data.get("total_records", "N/A"))],
            ["Generated By", "AI Financial Risk Assistant v1.0"],
        ]
        meta_table = Table(meta, colWidths=[150, 250])
        meta_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#333333")),
            ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#666666")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ]))
        elements.append(meta_table)

        return elements

    def _build_section(self, title: str, content: str) -> List:
        """Build a text section with header and body."""
        elements = []
        elements.append(Paragraph(title, self.styles["SectionHeader"]))
        for paragraph in content.split("\n"):
            if paragraph.strip():
                elements.append(Paragraph(paragraph.strip(), self.styles["BodyText2"]))
        elements.append(Spacer(1, 12))
        return elements

    def _build_list_section(self, title: str, items: List[str]) -> List:
        """Build a numbered list section."""
        elements = []
        elements.append(Paragraph(title, self.styles["SectionHeader"]))
        for i, item in enumerate(items, 1):
            elements.append(Paragraph(
                f"<b>{i}.</b> {item}",
                self.styles["BodyText2"],
            ))
        elements.append(Spacer(1, 12))
        return elements

    def _build_table_section(self, title: str, data: List[Dict]) -> List:
        """Build a section with a data table."""
        elements = []
        elements.append(Paragraph(title, self.styles["SectionHeader"]))

        if not data:
            elements.append(Paragraph("No data available.", self.styles["BodyText2"]))
            return elements

        # Build table from list of dicts
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([str(row.get(h, "")) for h in headers])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        return elements

    def _build_risk_section(self, risk_data: Dict) -> List:
        """Build risk trends section with metrics."""
        elements = []
        elements.append(Paragraph("Risk Trends Analysis", self.styles["SectionHeader"]))

        if isinstance(risk_data, str):
            elements.append(Paragraph(risk_data, self.styles["BodyText2"]))
        elif isinstance(risk_data, dict):
            for key, value in risk_data.items():
                elements.append(Paragraph(
                    f"<b>{key}:</b> {value}",
                    self.styles["BodyText2"],
                ))

        elements.append(Spacer(1, 12))
        return elements

    def _build_model_section(self, model_data: Dict) -> List:
        """Build model performance section."""
        elements = []
        elements.append(Paragraph("Model Performance", self.styles["SectionHeader"]))

        metrics = [
            ["Metric", "Value"],
            ["Model", model_data.get("model_name", "N/A")],
            ["Accuracy", f"{model_data.get('accuracy', 0):.4f}"],
            ["Precision", f"{model_data.get('precision', 0):.4f}"],
            ["Recall", f"{model_data.get('recall', 0):.4f}"],
            ["F1 Score", f"{model_data.get('f1_score', 0):.4f}"],
            ["ROC AUC", f"{model_data.get('roc_auc', 0):.4f}"],
        ]
        table = Table(metrics, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        return elements

    def _build_footer(self) -> List:
        """Build the report footer."""
        elements = []
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor("#cccccc"),
        ))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            f"Generated by AI Financial Risk & Collections Assistant | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confidential",
            ParagraphStyle(
                name="Footer",
                fontSize=8,
                textColor=colors.HexColor("#999999"),
                alignment=TA_CENTER,
            ),
        ))
        return elements
