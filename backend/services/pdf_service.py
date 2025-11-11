# backend/services/pdf_service.py
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether,
    Flowable,
)
from reportlab.pdfgen import canvas

BLUE = colors.HexColor("#2563eb")
BLUE_DARK = colors.HexColor("#1e40af")
CYAN = colors.HexColor("#06b6d4")
GREEN = colors.HexColor("#22c55e")
RED = colors.HexColor("#ef4444")
ORANGE = colors.HexColor("#fb923c")
GRAY_800 = colors.HexColor("#1f2937")
GRAY_600 = colors.HexColor("#4b5563")
GRAY_200 = colors.HexColor("#e5e7eb")
GRAY_BG = colors.HexColor("#f9fafb")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, url: str = "", generated: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[dict] = []
        self._url = url
        self._generated = generated

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(total_pages)
            super().showPage()
        super().save()

    def _draw_header_footer(self, total_pages: int):
        page_num = self._pageNumber
        # Skip header/footer on cover
        if page_num == 1:
            return
        self.setFont("Helvetica", 9)
        self.setFillColor(GRAY_600)
        header = f"QA Analysis Report | {self._url}"
        self.drawString(72, A4[1] - 40, header)
        footer = f"Page {page_num} of {total_pages} | Generated: {self._generated}"
        self.drawRightString(A4[0] - 72, 40, footer)

class PDFService:
    def generate_report(self, report_data: Dict, summary: str, performance: Dict, run_dir: Path) -> Path:
        """
        Generates a professionally styled PDF report using ReportLab.
        """
        pdf_path = run_dir / "QA_Report.pdf"
        url = report_data.get("url", "N/A")
        generated = datetime.now().strftime("%Y-%m-%d %H:%M")

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            leftMargin=72,
            rightMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="TitleWhite", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=colors.white, alignment=1, spaceAfter=12))
        styles.add(ParagraphStyle(name="H1", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=GRAY_800, spaceBefore=12, spaceAfter=20))
        styles.add(ParagraphStyle(name="H2", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=GRAY_800, spaceBefore=10, spaceAfter=6))
        styles.add(ParagraphStyle(name="Muted", fontName="Helvetica", fontSize=10, leading=14, textColor=GRAY_600))
        styles.add(ParagraphStyle(name="NormalDark", fontName="Helvetica", fontSize=10, leading=15, textColor=GRAY_800))
        styles.add(ParagraphStyle(name="Caption", fontName="Helvetica", fontSize=9, leading=12, textColor=GRAY_600, alignment=1))
        styles.add(ParagraphStyle(name="BadgeGreen", backColor=GREEN, textColor=colors.white, fontSize=9, leading=11, alignment=1, spaceAfter=4))
        styles.add(ParagraphStyle(name="BadgeRed", backColor=RED, textColor=colors.white, fontSize=9, leading=11, alignment=1, spaceAfter=4))
        styles.add(ParagraphStyle(name="SectionHeader", backColor=BLUE, textColor=colors.white, fontName="Helvetica-Bold", fontSize=13, leading=18, leftIndent=6, spaceBefore=16, spaceAfter=20))

        story: List = []
        self._figure_counter = 1

        # Cover page
        story.extend(self._build_cover(styles, url, generated))
        story.append(PageBreak())

        # Executive Summary
        story.extend(self._build_executive_summary(styles, summary, report_data))

        # Performance Section
        story.append(Paragraph("Performance", styles["SectionHeader"]))
        story.extend(self._build_performance(styles, performance))

        # Detailed Analysis per category
        for key, title in [
            ("color_analysis", "Color Analysis"),
            ("typography_analysis", "Typography Analysis"),
            ("layout_analysis", "Layout Analysis"),
            ("content_analysis", "Content Analysis"),
        ]:
            cat = report_data.get(key)
            if not isinstance(cat, dict):
                continue
            story.append(Spacer(1, 8))
            story.extend(self._build_category(styles, title, cat, run_dir))

        # Screenshots (if any collected via issues)
        shots = self._collect_issue_screenshots(report_data, run_dir)
        if shots:
        story.append(PageBreak())
            story.append(Paragraph("Screenshots", styles["H1"]))
            for shot_path, caption in shots:
                if shot_path and shot_path.exists():
                    story.extend(self._image_block(styles, shot_path, f"Figure {self._figure_counter}: {caption}"))
                    self._figure_counter += 1
                else:
                    story.append(Paragraph(f"Figure {self._figure_counter}: {caption} (screenshot file not found)", styles["Muted"]))
                    self._figure_counter += 1

        # Build with numbered header/footer
        doc.build(
            story,
            canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, url=url, generated=generated, **kwargs),
        )
        return pdf_path

    def _build_cover(self, styles, url: str, generated: str) -> List:
        items: List = []
        from reportlab.platypus import Table
        title = "Website QA Analysis Report"

        # Full width centered band
        band = Table(
            [[Paragraph(title, styles["TitleWhite"])]],
            colWidths=[A4[0] - 144],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), BLUE_DARK),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 24),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 24),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ],
        )
        items.append(band)
        items.append(Spacer(1, 20))

        # URL in colored box centered
        url_box = Table(
            [[Paragraph(url, ParagraphStyle(name="url", fontName="Helvetica-Bold", fontSize=12, textColor=colors.white))]],
            colWidths=[A4[0] - 240],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), BLUE),
                ("BOX", (0, 0), (-1, -1), 0.5, BLUE),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ],
        )
        items.append(url_box)
        items.append(Spacer(1, 12))
        items.append(Paragraph(f"Generated: {generated}", styles["Muted"]))
        return items

    def _build_executive_summary(self, styles, summary: str, report_data: Dict) -> List:
        items: List = []
        items.append(Paragraph("Executive Summary", styles["H1"]))
        # Issue counts
        counts = self._count_issues_by_impact(report_data)
        total = counts["total"]

        # Summary box (light blue background)
        content = []
        key_style = ParagraphStyle(name="Key", fontName="Helvetica-Bold", fontSize=11, textColor=GRAY_800, leading=16)
        p_style = styles["NormalDark"]

        if summary:
            # Parse structured markdown summary
            lines = summary.split("\n")
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Headers
                if line.startswith("# "):
                    # Main header - already have "Executive Summary" above
                    continue
                elif line.startswith("## "):
                    # Section header
                    section_text = line.replace("## ", "").strip()
                    content.append(Spacer(1, 8))
                    content.append(Paragraph(f"<b>{section_text}</b>", styles["H2"]))
                elif line.startswith("### "):
                    # Subsection header
                    subsection_text = line.replace("### ", "").strip()
                    content.append(Spacer(1, 6))
                    content.append(Paragraph(f"<b>{subsection_text}</b>", styles["H2"]))
                elif line.startswith("- ") or line.startswith("* "):
                    # List item
                    item_text = line[2:].strip()
                    content.append(Paragraph(f"• {item_text}", p_style))
                    content.append(Spacer(1, 3))
                elif line.startswith("  - ") or line.startswith("  * "):
                    # Nested list item
                    item_text = line[4:].strip()
                    content.append(Paragraph(f"  • {item_text}", p_style))
                    content.append(Spacer(1, 2))
                elif line.startswith(tuple("123456789")):
                    # Numbered list
                    content.append(Paragraph(line, p_style))
                    content.append(Spacer(1, 3))
                else:
                    # Regular paragraph
                    content.append(Paragraph(line, p_style))
                    content.append(Spacer(1, 4))

        metrics_row = Table(
            [[
                Paragraph(f"<font color='{GREEN}'>Good</font>", key_style),
                Paragraph(f"<font color='{RED}'>Issues</font>", key_style),
                Paragraph("Total Issues", key_style),
            ],
             [
                Paragraph(str(max(0, 0)), styles["NormalDark"]),
                Paragraph(str(total), styles["NormalDark"]),
                Paragraph(f"<para align='center'><font size=16><b>{total}</b></font></para>", styles["NormalDark"]),
            ]],
            colWidths=[120, 120, 240],
            style=[
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                ("ALIGN", (0, 1), (1, 1), "LEFT"),
                ("ALIGN", (2, 1), (2, 1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ],
        )

        box = Table(
            [[content], [metrics_row]],
            colWidths=[A4[0] - 144],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), GRAY_BG),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#bfdbfe")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ],
        )
        items.append(box)
        items.append(Spacer(1, 15))
        return items

    def _build_performance(self, styles, performance: Dict) -> List:
        items: List = []
        if not performance or not performance.get("success"):
            items.append(Paragraph("Performance data unavailable.", styles["Muted"]))
            return items
        metrics = performance.get("metrics", {})
        data = [["Metric", "Score / Value"]]
        score_keys = ["performance_score", "accessibility_score", "best_practices_score", "seo_score"]
        for key in score_keys + ["first_contentful_paint", "largest_contentful_paint", "speed_index"]:
            label = key.replace("_", " ").title()
            val = metrics.get(key, "N/A")
            data.append([label, str(val)])
        table = Table(data, colWidths=[240, 260])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                    ("GRID", (0, 0), (-1, -1), 0.25, GRAY_200),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRAY_BG]),
                    ("RIGHTPADDING", (1, 1), (1, -1), 8),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 1), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ]
            )
        )
        # Color-code score rows
        for r, key in enumerate(score_keys, start=1):
            val = metrics.get(key, None)
            if isinstance(val, (int, float)):
                color = GREEN if val >= 90 else ORANGE if val >= 70 else RED
                table.setStyle(TableStyle([("TEXTCOLOR", (1, r), (1, r), color)]))
        items.append(table)
        return items

    def _build_category(self, styles, title: str, cat: Dict, run_dir: Path) -> List:
        items: List = []
        # Header with status badge
        items.append(Paragraph(title, styles["H1"]))
        status = (cat.get("status") or "").strip().lower()
        badge_style = styles["BadgeGreen"] if status == "match" else styles["BadgeRed"]
        badge_text = "✓ MATCH" if status == "match" else "✗ MISMATCH"
        items.append(Paragraph(badge_text, badge_style))
        if cat.get("details"):
            items.append(Paragraph(cat["details"], styles["NormalDark"]))

        # Issues table (if any)
        issues = cat.get("issues") or []
        if issues:
            # Use Paragraph objects for headers to prevent text overlap
            header_style = ParagraphStyle(
                name="TableHeader",
                fontName="Helvetica-Bold",
                fontSize=9,
                textColor=colors.white,
                leading=11
            )
            data = [[
                Paragraph("<b>Description</b>", header_style),
                Paragraph("<b>Expected</b>", header_style),
                Paragraph("<b>Found</b>", header_style),
                Paragraph("<b>Location</b>", header_style),
                Paragraph("<b>Impact</b>", header_style),
                Paragraph("<b>Doc Page</b>", header_style)
            ]]
            
            # Use Paragraph objects for cell content to enable text wrapping
            cell_style = ParagraphStyle(
                name="TableCell",
                fontName="Helvetica",
                fontSize=8,
                textColor=GRAY_800,
                leading=10,
                leftIndent=0,
                rightIndent=0
            )
            
            for i in issues:
                desc = str(i.get("description", ""))[:90]  # Truncate if too long
                expected = str(i.get("expected_value", i.get("expected", "")))[:35]
                found = str(i.get("found_value", i.get("found", "")))[:35]
                location = str(i.get("selector", i.get("location", "not available")))[:20]
                impact = str(i.get("impact", "")).title()
                doc_page = str(i.get("doc_page", ""))[:18]
                
                data.append([
                    Paragraph(desc, cell_style),
                    Paragraph(expected, cell_style),
                    Paragraph(found, cell_style),
                    Paragraph(location, cell_style),
                    Paragraph(impact, cell_style),
                    Paragraph(doc_page, cell_style),
                ])
            
            # Adjusted column widths to prevent overlap (total = 468pt for A4 - 144pt margins)
            table = Table(data, colWidths=[160, 95, 95, 50, 40, 28])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), CYAN),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("GRID", (0, 0), (-1, -1), 0.25, GRAY_200),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("TOPPADDING", (0, 1), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                        ("LEFTPADDING", (0, 1), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 1), (-1, -1), 3),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),  # Top align to prevent overlap
                    ]
                )
            )
            # Impact color-coding
            for r in range(1, len(data)):
                impact_text = str(data[r][4] or "").strip().lower()
                color = RED if impact_text == "high" else ORANGE if impact_text == "medium" else colors.HexColor("#f59e0b") if impact_text == "low" else GRAY_800
                table.setStyle(TableStyle([("TEXTCOLOR", (4, r), (4, r), color)]))
            items.append(Spacer(1, 6))
            items.append(table)

            # Inline screenshots under table
            for idx, i in enumerate(issues, 1):
                shot_rel = i.get("screenshot")
                if not shot_rel:
                    continue
                shot_path = (run_dir / shot_rel).resolve()
                if shot_path.exists():
                    caption = i.get("description", f"Issue {idx}")
                    items.extend(self._image_block(styles, shot_path, caption))
        return items

    def _image_block(self, styles, image_path: Path, caption: str) -> List:
        items: List = []
        try:
            # Scale image to max width 500px, keep aspect
            max_w = 500
            img = Image(str(image_path))
            iw, ih = img.wrap(0, 0)
            scale = min(1.0, max_w / (iw or max_w))
            img.drawWidth = (iw or max_w) * scale
            img.drawHeight = (ih or (max_w * 0.6)) * scale
            # Center with 2pt border and 10pt padding
            img_table = Table([[img]], colWidths=[img.drawWidth])
            img_table.setStyle(
                TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 2, GRAY_200),
                        ("TOPPADDING", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ]
                )
            )
            container = Table([[img_table]], colWidths=[A4[0] - 144])
            container.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
            items.append(Spacer(1, 10))
            items.append(container)
            items.append(Paragraph(caption, styles["Caption"]))
        except Exception:
            # If the image fails to load, skip gracefully
            pass
        return items

    def _count_issues_by_impact(self, report_data: Dict) -> Dict[str, int]:
        """Count issues by impact level."""
        counts = {"high": 0, "medium": 0, "low": 0, "total": 0}
        for key in ["color_analysis", "typography_analysis", "layout_analysis", "content_analysis"]:
            cat = report_data.get(key, {})
            for issue in cat.get("issues", []) or []:
                impact = (issue.get("impact") or "").strip().lower()
                if impact in counts:
                    counts[impact] += 1
                counts["total"] += 1
        return counts
    
    def _collect_issue_screenshots(self, report_data: Dict, run_dir: Path) -> List[tuple[Path, str]]:
        shots: List[tuple[Path, str]] = []
        for key in ["color_analysis", "typography_analysis", "layout_analysis", "content_analysis"]:
            cat = report_data.get(key, {})
            for issue in cat.get("issues", []) or []:
                shot_rel = issue.get("screenshot")
                if not shot_rel:
                    continue
                p = (run_dir / shot_rel).resolve()
                if p.exists():
                    shots.append((p, issue.get("description", key.replace("_", " ").title())))
        return shots