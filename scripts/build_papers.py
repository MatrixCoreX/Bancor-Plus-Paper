#!/usr/bin/env python3
from __future__ import annotations

import math
import os
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("BANCOR_PLUS_OUTPUT_DIR", REPOSITORY_ROOT))
ZH_OUTPUT = OUTPUT_DIR / "Bancor_Plus_技术论文_中文版.pdf"
EN_OUTPUT = OUTPUT_DIR / "Bancor_Plus_Technical_Paper_English.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 20 * mm
MARGIN_RIGHT = 20 * mm
MARGIN_TOP = 20 * mm
MARGIN_BOTTOM = 18 * mm

INK = HexColor("#172033")
MUTED = HexColor("#5E6B7A")
BLUE = HexColor("#246BCE")
CYAN = HexColor("#19A7AE")
PALE_BLUE = HexColor("#EAF2FF")
PALE_CYAN = HexColor("#EAF8F8")
PALE_GRAY = HexColor("#F4F6F8")
GRID = HexColor("#D8E0E9")
WARNING = HexColor("#9A5B13")


def resolve_font(env_name: str, *candidates: str) -> str:
    configured = os.environ.get(env_name)
    paths = ([configured] if configured else []) + list(candidates)
    for path in paths:
        if path and Path(path).is_file():
            return path
    raise FileNotFoundError(
        f"No usable font found for {env_name}. Set {env_name} to an installed font file."
    )


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(
        "NotoSans",
        resolve_font(
            "BANCOR_PLUS_FONT_REGULAR",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/Library/Fonts/NotoSans-Regular.ttf",
        ),
    ))
    pdfmetrics.registerFont(TTFont(
        "NotoSans-Bold",
        resolve_font(
            "BANCOR_PLUS_FONT_BOLD",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/Library/Fonts/NotoSans-Bold.ttf",
        ),
    ))
    pdfmetrics.registerFont(TTFont(
        "NotoMono",
        resolve_font(
            "BANCOR_PLUS_FONT_MONO",
            "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
            "/Library/Fonts/NotoSansMono-Regular.ttf",
        ),
    ))
    pdfmetrics.registerFont(TTFont(
        "NotoCJK",
        resolve_font(
            "BANCOR_PLUS_FONT_CJK",
            str(REPOSITORY_ROOT / "fonts" / "NotoSansSC-Medium.ttf"),
            "/Library/Fonts/NotoSansSC-Medium.ttf",
        ),
    ))
    pdfmetrics.registerFont(TTFont(
        "NotoCJK-Bold",
        resolve_font(
            "BANCOR_PLUS_FONT_CJK_BOLD",
            str(REPOSITORY_ROOT / "fonts" / "NotoSansSC-Bold.ttf"),
            "/Library/Fonts/NotoSansSC-Bold.ttf",
        ),
    ))


def styles_for(language: str) -> dict[str, ParagraphStyle]:
    is_zh = language == "zh"
    body_font = "NotoCJK" if is_zh else "NotoSans"
    bold_font = "NotoCJK-Bold" if is_zh else "NotoSans-Bold"
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PaperTitle",
            parent=base["Title"],
            fontName=bold_font,
            fontSize=25,
            leading=34,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=7 * mm,
        ),
        "subtitle": ParagraphStyle(
            "PaperSubtitle",
            parent=base["Normal"],
            fontName=body_font,
            fontSize=11.5,
            leading=18,
            textColor=MUTED,
            spaceAfter=4 * mm,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            parent=base["Normal"],
            fontName=body_font,
            fontSize=9.5,
            leading=15,
            textColor=MUTED,
        ),
        "abstract_label": ParagraphStyle(
            "AbstractLabel",
            parent=base["Heading2"],
            fontName=bold_font,
            fontSize=13,
            leading=18,
            textColor=BLUE,
            spaceBefore=2 * mm,
            spaceAfter=2 * mm,
        ),
        "body": ParagraphStyle(
            "PaperBody",
            parent=base["BodyText"],
            fontName=body_font,
            fontSize=9.6 if is_zh else 9.3,
            leading=16 if is_zh else 14.2,
            textColor=INK,
            alignment=TA_LEFT if is_zh else TA_JUSTIFY,
            spaceAfter=(2.6 if is_zh else 2.2) * mm,
            allowWidows=0,
            allowOrphans=0,
        ),
        "body_small": ParagraphStyle(
            "PaperBodySmall",
            parent=base["BodyText"],
            fontName=body_font,
            fontSize=8.3,
            leading=13,
            textColor=MUTED,
            spaceAfter=1.5 * mm,
        ),
        "h1": ParagraphStyle(
            "Heading1Paper",
            parent=base["Heading1"],
            fontName=bold_font,
            fontSize=16,
            leading=22,
            textColor=INK,
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "Heading2Paper",
            parent=base["Heading2"],
            fontName=bold_font,
            fontSize=12,
            leading=17,
            textColor=BLUE,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "Heading3Paper",
            parent=base["Heading3"],
            fontName=bold_font,
            fontSize=10.3,
            leading=15,
            textColor=CYAN,
            spaceBefore=3 * mm,
            spaceAfter=1.5 * mm,
            keepWithNext=True,
        ),
        "toc": ParagraphStyle(
            "TOCEntry",
            parent=base["Normal"],
            fontName=body_font,
            fontSize=7.8,
            leading=10.2,
            textColor=INK,
        ),
        "formula": ParagraphStyle(
            "Formula",
            parent=base["Code"],
            fontName="NotoMono",
            fontSize=8.4,
            leading=14,
            textColor=INK,
            leftIndent=4 * mm,
            rightIndent=4 * mm,
            spaceBefore=1.5 * mm,
            spaceAfter=1.5 * mm,
        ),
        "caption": ParagraphStyle(
            "FigureCaption",
            parent=base["Normal"],
            fontName=body_font,
            fontSize=8,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceBefore=1 * mm,
            spaceAfter=3 * mm,
        ),
        "table": ParagraphStyle(
            "TableText",
            parent=base["Normal"],
            fontName=body_font,
            fontSize=7.8,
            leading=11.5,
            textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "TableHead",
            parent=base["Normal"],
            fontName=bold_font,
            fontSize=7.8,
            leading=11.5,
            textColor=colors.white,
            alignment=TA_LEFT,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName=body_font,
            fontSize=9.2,
            leading=15,
            textColor=INK,
            spaceAfter=0,
        ),
        "reference": ParagraphStyle(
            "Reference",
            parent=base["BodyText"],
            fontName=body_font,
            fontSize=6.8,
            leading=9.2,
            textColor=INK,
            leftIndent=5 * mm,
            firstLineIndent=-5 * mm,
            spaceAfter=1 * mm,
        ),
    }


class PaperDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, language: str, paper_title: str, **kwargs):
        super().__init__(filename, **kwargs)
        self.language = language
        self.paper_title = paper_title
        self._heading_counter = 0
        frame = Frame(
            MARGIN_LEFT,
            MARGIN_BOTTOM,
            PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT,
            PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM,
            id="normal",
        )
        self.addPageTemplates(PageTemplate(id="paper", frames=[frame], onPage=self.draw_page))

    def beforeDocument(self):
        self._heading_counter = 0

    def draw_page(self, canvas, doc):
        page = canvas.getPageNumber()
        if page == 1:
            return
        canvas.saveState()
        body_font = "NotoCJK" if self.language == "zh" else "NotoSans"
        canvas.setStrokeColor(GRID)
        canvas.setLineWidth(0.35)
        canvas.line(MARGIN_LEFT, PAGE_HEIGHT - 12 * mm, PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 12 * mm)
        canvas.setFont(body_font, 7.3)
        canvas.setFillColor(MUTED)
        header = "Bancor Plus 技术论文" if self.language == "zh" else "Bancor Plus Technical Paper"
        canvas.drawString(MARGIN_LEFT, PAGE_HEIGHT - 9 * mm, header)
        canvas.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 9 * mm, "2026-09-28")
        canvas.line(MARGIN_LEFT, 12 * mm, PAGE_WIDTH - MARGIN_RIGHT, 12 * mm)
        canvas.drawCentredString(PAGE_WIDTH / 2, 7.5 * mm, str(page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style in {"Heading1Paper", "Heading2Paper", "Heading3Paper"}:
                level = {"Heading1Paper": 0, "Heading2Paper": 1, "Heading3Paper": 2}[style]
                text = flowable.getPlainText()
                key = f"heading-{self._heading_counter}"
                self._heading_counter += 1
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify("TOCEntry", (level, text, self.page, key))


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=4 * mm) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=6 * mm,
        bulletFontName=style.fontName,
        bulletFontSize=6,
        bulletColor=BLUE,
        spaceAfter=2 * mm,
    )


def formula_box(lines: list[str], style: ParagraphStyle) -> Table:
    text = "\n".join(lines)
    table = Table([[Preformatted(text, style)]], colWidths=[PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.6, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    return table


def callout(text: str, style: ParagraphStyle, color: colors.Color = PALE_BLUE) -> Table:
    table = Table([[Paragraph(text, style)]], colWidths=[PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
        ("BOX", (0, 0), (-1, -1), 0.4, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    return table


def styled_table(rows: list[list[str]], widths: list[float], st: dict[str, ParagraphStyle]) -> Table:
    cells = []
    for row_index, row in enumerate(rows):
        cells.append([
            Paragraph(escape(str(value)), st["table_head"] if row_index == 0 else st["table"])
            for value in row
        ])
    table = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_GRAY]),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    return table


def reserve_curve_figure(language: str) -> Drawing:
    width, height = 165 * mm, 67 * mm
    drawing = Drawing(width, height)
    left, bottom = 18 * mm, 12 * mm
    plot_w, plot_h = width - 28 * mm, height - 20 * mm
    drawing.add(Rect(0, 0, width, height, rx=7, ry=7, fillColor=PALE_GRAY, strokeColor=GRID))
    drawing.add(Line(left, bottom, left, bottom + plot_h, strokeColor=MUTED, strokeWidth=0.8))
    drawing.add(Line(left, bottom, left + plot_w, bottom, strokeColor=MUTED, strokeWidth=0.8))
    for i in range(1, 5):
        y = bottom + plot_h * i / 5
        drawing.add(Line(left, y, left + plot_w, y, strokeColor=GRID, strokeWidth=0.35))
    points = []
    for i in range(101):
        u = 2.0 * i / 100
        fraction = u / (1.0 + u)
        points.extend([left + plot_w * u / 2.0, bottom + plot_h * fraction / (2.0 / 3.0)])
    drawing.add(PolyLine(points, strokeColor=BLUE, strokeWidth=2.2))
    x_label = "交易规模 / 输入储备" if language == "zh" else "Trade size / input reserve"
    y_label = "输出 / 输出储备" if language == "zh" else "Output / output reserve"
    curve_label = "z/Rout = u/(1+u)" if language == "en" else "z/Rout = u/(1+u)"
    drawing.add(String(left + plot_w / 2, 4 * mm, x_label, fontName="NotoCJK" if language == "zh" else "NotoSans", fontSize=7, textAnchor="middle", fillColor=MUTED))
    drawing.add(String(3 * mm, bottom + plot_h / 2, y_label, fontName="NotoCJK" if language == "zh" else "NotoSans", fontSize=7, fillColor=MUTED))
    drawing.add(String(left + plot_w * 0.63, bottom + plot_h * 0.68, curve_label, fontName="NotoMono", fontSize=7.5, fillColor=BLUE))
    return drawing


def injection_figure(language: str) -> Drawing:
    width, height = 165 * mm, 66 * mm
    drawing = Drawing(width, height)
    left, bottom = 18 * mm, 12 * mm
    plot_w, plot_h = width - 28 * mm, height - 20 * mm
    drawing.add(Rect(0, 0, width, height, rx=7, ry=7, fillColor=PALE_CYAN, strokeColor=GRID))
    drawing.add(Line(left, bottom, left, bottom + plot_h, strokeColor=MUTED, strokeWidth=0.8))
    drawing.add(Line(left, bottom, left + plot_w, bottom, strokeColor=MUTED, strokeWidth=0.8))
    for i in range(1, 5):
        x = left + plot_w * i / 5
        drawing.add(Line(x, bottom, x, bottom + plot_h, strokeColor=GRID, strokeWidth=0.35))
        y = bottom + plot_h * i / 5
        drawing.add(Line(left, y, left + plot_w, y, strokeColor=GRID, strokeWidth=0.35))
    points = []
    for i in range(101):
        severity = i / 100
        rate = 0.1 + 0.9 * severity
        points.extend([left + plot_w * severity, bottom + plot_h * rate])
    drawing.add(PolyLine(points, strokeColor=CYAN, strokeWidth=2.2))
    current_x = 0.43633852
    current_rate = 0.49270466
    cx = left + plot_w * current_x
    cy = bottom + plot_h * current_rate
    drawing.add(Circle(cx, cy, 3.2, fillColor=BLUE, strokeColor=colors.white, strokeWidth=1))
    body_font = "NotoCJK" if language == "zh" else "NotoSans"
    snapshot_label = "测试数据快照" if language == "zh" else "Test-data snapshot"
    drawing.add(String(cx + 4, cy + 3, snapshot_label, fontName=body_font, fontSize=6.5, fillColor=BLUE))
    x_label = "缺口严重度 e" if language == "zh" else "Gap severity e"
    y_label = "注入比例 r" if language == "zh" else "Injection rate r"
    drawing.add(String(left + plot_w / 2, 4 * mm, x_label, fontName=body_font, fontSize=7, textAnchor="middle", fillColor=MUTED))
    drawing.add(String(3 * mm, bottom + plot_h / 2, y_label, fontName=body_font, fontSize=7, fillColor=MUTED))
    drawing.add(String(left + plot_w * 0.58, bottom + plot_h * 0.75, "r = 0.1% + 0.9% e", fontName="NotoMono", fontSize=7.2, fillColor=CYAN))
    return drawing


def architecture_figure(language: str) -> Drawing:
    width, height = 165 * mm, 64 * mm
    drawing = Drawing(width, height)
    drawing.add(Rect(0, 0, width, height, rx=7, ry=7, fillColor=colors.white, strokeColor=GRID))
    body_font = "NotoCJK" if language == "zh" else "NotoSans"
    bold_font = "NotoCJK-Bold" if language == "zh" else "NotoSans-Bold"
    labels = (
        ["AI 节点首次参与", "组织参与资金池", "动态注入控制器", "Bancor Plus 储备池", "交易与报价", "审计账本与价格 K 线"]
        if language == "zh"
        else ["AI participation", "Participation fund", "Adaptive controller", "Bancor Plus reserves", "Trades and quotes", "Audit ledger and price candles"]
    )
    positions = [(8, 39), (58, 39), (108, 39), (108, 11), (58, 11), (8, 11)]
    box_w, box_h = 43 * mm, 14 * mm
    for index, ((x_mm, y_mm), label) in enumerate(zip(positions, labels)):
        fill = PALE_BLUE if index in {0, 1, 3, 4} else PALE_CYAN
        drawing.add(Rect(x_mm * mm, y_mm * mm, box_w, box_h, rx=5, ry=5, fillColor=fill, strokeColor=GRID))
        drawing.add(String(x_mm * mm + box_w / 2, y_mm * mm + 5.5 * mm, label, fontName=bold_font, fontSize=7.2, textAnchor="middle", fillColor=INK))
    arrows = [
        ((51, 46), (58, 46)), ((101, 46), (108, 46)), ((129.5, 39), (129.5, 25)),
        ((108, 18), (101, 18)), ((58, 18), (51, 18)), ((29.5, 25), (29.5, 39)),
    ]
    for (x1, y1), (x2, y2) in arrows:
        drawing.add(Line(x1 * mm, y1 * mm, x2 * mm, y2 * mm, strokeColor=BLUE, strokeWidth=1.3))
        angle = math.atan2(y2 - y1, x2 - x1)
        size = 2.3 * mm
        ax, ay = x2 * mm, y2 * mm
        points = [
            ax, ay,
            ax - size * math.cos(angle - 0.45), ay - size * math.sin(angle - 0.45),
            ax - size * math.cos(angle + 0.45), ay - size * math.sin(angle + 0.45),
        ]
        from reportlab.graphics.shapes import Polygon
        drawing.add(Polygon(points, fillColor=BLUE, strokeColor=BLUE))
    return drawing


def cover_story(language: str, st: dict[str, ParagraphStyle]) -> list:
    if language == "zh":
        title = "Bancor Plus：<br/>AI 时代面向企业与团队的储备曲线算法"
        subtitle = "以连续流动性连接 AI 贡献奖励、组织预算、动态储备注入与可审计结算"
        meta = "技术研究论文 | 测试数据快照 | 中文版"
        note = (
            "本文所称 Bancor Plus 是本系统对自身增强型储备曲线市场的命名，"
            "不代表 Bancor 官方版本序列。文中 USD 为系统内部记账单位，不构成法币兑付承诺。"
        )
        abstract_label = "摘要"
        abstract = (
            "Bancor 早期提出以储备资产和连续定价公式替代订单簿中的同步对手方匹配，"
            "为自动做市与长尾资产流动性提供了早期系统化框架。本文首先梳理 Bancor 名称与"
            "连续流动性思想的起源，解释恒定储备比、交易规模相关的有效价格以及双储备转换器。"
            "随后面向 AI 时代的企业与团队，分析 Bancor Plus 的当前实现：AIC/USD 双储备精确输入曲线、"
            "版本化报价、签名授权、原子账本、组织参与资金池，以及一种按储备缺口自适应调节的"
            "USD 单边注入控制器。该控制器以目标占比、平衡缓冲区、比例上下限和单次池增幅上限"
            "共同约束注入量；注入改变池内边际价格与可售深度，但不生成交易、手续费、成交量或"
            "AIC 流动。该架构可把 AI 算力、模型服务、数据贡献和项目协作形成的内部奖励连接到可计算的"
            "组织流动性。在此基础上，本文提出一个以已结算 AI 业务收入和交易手续费为来源的利润分配层："
            "先扣除成本、负债和风险准备，再把可分配利润按流动性、团队、用户与留存四类用途划分，并以"
            "可核验贡献分数完成个体分配。本文将 Bancor 明确定义为与运行载体无关的储备算法，并把数据库结算、"
            "链上合约与混合部署作为独立执行层讨论。本文给出公式推导、测试数据参数快照、数值案例、稳定性分析、审计边界和风险限制。"
        )
        keywords = "关键词：Bancor；企业 AI；团队激励；内部价值交换；储备曲线；动态流动性；可审计账本"
    else:
        title = "Bancor Plus: A Reserve-Curve Algorithm for Enterprises and Teams in the AI Era"
        subtitle = "Connecting AI contribution rewards, organizational budgets, adaptive reserves, and auditable settlement"
        meta = "Technical research paper | Test-data snapshot | English edition"
        note = (
            "Bancor Plus is the name used in this system for its enhanced reserve-curve market. "
            "It does not denote an official Bancor version. USD is an internal accounting unit and carries no promise of fiat redemption."
        )
        abstract_label = "Abstract"
        abstract = (
            "Bancor introduced an early systematic model for replacing synchronous order matching with reserve assets and continuously "
            "computed prices. This paper traces the origin of that idea, explains constant reserve ratios, transaction-size-dependent "
            "execution, and two-reserve conversion, and then applies the current Bancor Plus implementation to enterprises and teams in the AI era. "
            "Bancor Plus combines an AIC/USD "
            "exact-input reserve curve with versioned quotes, signed authorization, atomic ledgers, a "
            "participation fund, and an adaptive controller for one-sided USD reserve additions. The controller jointly applies a target "
            "share, a balance buffer, minimum and maximum rates, and a per-step reserve-growth cap. A reserve addition changes marginal price "
            "and sell-side depth but creates no trade, fee, volume, or AIC flow. The architecture links internal rewards for AI compute, model "
            "services, data contributions, and project collaboration to computable organizational liquidity. On top of this market layer, the paper "
            "proposes a profit-distribution layer funded only by settled AI-business revenue and trading fees. After costs, liabilities, and risk reserves, "
            "distributable profit is divided among liquidity, teams, users, and retained earnings, then assigned through verifiable contribution scores. "
            "The paper defines Bancor as a reserve algorithm independent of its execution medium, and discusses database settlement, on-chain "
            "contracts, and hybrid deployment as a separate execution layer. It derives the formulas, documents the test-data policy "
            "snapshot, works through numerical examples, and evaluates convergence, observability, auditability, and limitations."
        )
        keywords = "Keywords: Bancor; enterprise AI; team incentives; internal value exchange; reserve curve; adaptive liquidity; auditable ledger"

    story = [
        Spacer(1, 23 * mm),
        Paragraph(title, st["title"]),
        Paragraph(subtitle, st["subtitle"]),
        Spacer(1, 6 * mm),
        HRFlowable(width="100%", thickness=2, color=BLUE, spaceBefore=2 * mm, spaceAfter=8 * mm),
        Paragraph(meta, st["cover_meta"]),
        Spacer(1, 18 * mm),
        Paragraph(abstract_label, st["abstract_label"]),
        Paragraph(abstract, st["body"]),
        Paragraph(keywords, st["body_small"]),
        Spacer(1, 8 * mm),
        callout(note, st["callout"], PALE_CYAN),
        PageBreak(),
    ]
    return story


def toc_story(language: str, st: dict[str, ParagraphStyle]) -> list:
    title = "目录" if language == "zh" else "Contents"
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("TOC0", parent=st["toc"], fontName=st["h1"].fontName, leftIndent=0, firstLineIndent=0, spaceBefore=0.5 * mm),
        ParagraphStyle("TOC1", parent=st["toc"], leftIndent=7 * mm, firstLineIndent=0),
        ParagraphStyle("TOC2", parent=st["toc"], leftIndent=14 * mm, firstLineIndent=0, fontSize=7.3),
    ]
    return [Paragraph(title, st["h1"]), Spacer(1, 3 * mm), toc, PageBreak()]


def heading(text: str, level: int, st: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(text, st[f"h{level}"])


def references_heading(text: str, st: dict[str, ParagraphStyle]) -> Paragraph:
    # Visually match a first-level heading without consuming a nearly empty
    # second contents page for one final references entry.
    return Paragraph(text, ParagraphStyle("ReferencesHeading", parent=st["h1"]))


def section_zh(st: dict[str, ParagraphStyle]) -> list:
    body = st["body"]
    story = []
    story += [
        heading("1. 引言", 1, st),
        paragraph(
            "流动性的核心困难不是资产能否被记录，而是交易者能否在没有同时出现反向订单时获得可预期的兑换结果。"
            "传统订单簿依赖买卖双方在价格与时间上相遇；储备曲线市场则让交易者直接面对一组资产储备和公开公式。"
            "这种机制不消除风险，但把部分流动性问题转化为可计算、可验证的状态转换。",
            body,
        ),
        paragraph(
            "AI 时代的企业与团队会同时面对两类问题：如何把算力、模型、数据、交付和用户参与转化为统一的内部奖励；"
            "以及如何让奖励资产具有连续、可解释的兑换能力。Bancor Plus 延续储备驱动兑换，并针对内部 USD 记账、"
            "参与者增长、利润分配和长期卖出压力，引入独立资金池与动态单边注入。它不是通用交易所、稳定币或法币"
            "通道，也不等同于某一种链或账本，而是一个具有明确运行边界的组织结算与激励算法。",
            body,
        ),
        callout(
            "研究问题：当企业和团队持续发放 AI 贡献奖励时，如何在不伪造成交、不把资本注入误记为利润、"
            "不无限制注资的前提下，维持兑换深度，并把真实利润透明地奖励给团队成员与用户？",
            st["callout"],
        ),

        heading("2. Bancor 的起源与基本思想", 1, st),
        heading("2.1 名称与问题意识", 2, st),
        paragraph(
            "Bancor 这一名称源自约翰·梅纳德·凯恩斯在第二次世界大战时期提出的超国家清算货币设想。Bancor 协议的"
            "原始论文借用该名称，关注的不是国际清算制度本身，而是数字代币之间的流动性与兑换问题。"
            "原始论文将传统交易中的“双重需求巧合”视为长尾货币难以流动的重要原因，并提出基于储备状态、"
            "按公式持续给出价格的 Smart Token 模型；智能合约是其早期描述中的执行载体，而不是公式成立的前提。[1]",
            body,
        ),
        heading("2.2 恒定储备比与连续价格", 2, st),
        paragraph(
            "原始模型用储备余额 R、Smart Token 供应量 S 和恒定储备比 CRR 表示瞬时价格。价格会在每次购买或"
            "赎回后重算，因此价格发现沿时间异步发生，不需要买单和卖单在同一时刻匹配。[1]",
            body,
        ),
        formula_box([
            "P = R / (S * CRR)",
            "Purchase: DeltaS = S * ((1 + DeltaR / R)^CRR - 1)",
            "Liquidation: DeltaR = R * (1 - (1 - DeltaS / S)^(1 / CRR))",
        ], st["formula"]),
        paragraph(
            "交易被视为无穷多个微小增量的积分，因此有效价格取决于交易规模。大额交易沿曲线移动更远，滑点更大；"
            "更深的储备降低同等交易规模造成的价格变化。",
            body,
        ),
        heading("2.3 双储备转换器", 2, st),
        paragraph(
            "当一个转换器同时持有两种储备资产，交易可以先抽象为进入中间供应，再退出另一侧。对于对称的双储备"
            "情形，可写成更直接的精确输入公式。设输入储备为 Rin，输出储备为 Rout，净输入为 q，输出为 z：",
            body,
        ),
        formula_box([
            "z = q * Rout / (Rin + q)",
            "(Rin + q) * (Rout - z) = Rin * Rout",
            "p_marginal = R_USD / R_AIC",
        ], st["formula"]),
        paragraph(
            "上式保持两侧储备乘积不变，属于恒定函数自动做市的一种两资产形式。现代研究将这类"
            "机制统一描述为由储备状态和交易函数决定可接受交易的 CFMM，并分析了其价格、储备不可耗尽边界与"
            "路径性质。[2][3]",
            body,
        ),
        reserve_curve_figure("zh"),
        paragraph("图 1. 归一化精确输入曲线。交易规模越大，输出继续增加，但边际输出递减。", st["caption"]),

        heading("3. Bancor 算法与运行载体的分离", 1, st),
        heading("3.1 算法层：只定义状态转换", 2, st),
        paragraph(
            "Bancor 首先是一组储备定价与状态转换算法。它读取储备、供应量或双储备余额以及交易输入，计算报价、"
            "输出、价格影响和交易后的新状态。只要初始状态、参数和输入相同，算法结果就应相同；这一性质不依赖"
            "数据库、智能合约、区块链或其他账本。",
            body,
        ),
        styled_table([
            ["算法要素", "内容", "不负责的事项"],
            ["状态", "储备余额、供应量、费率与控制参数", "状态存在哪里、由谁托管"],
            ["输入", "交易方向、输入金额、最低到账等约束", "用户身份认证与权限管理"],
            ["计算", "连续价格、输出、价格影响与新储备", "签名格式、网络确认和数据库协议"],
            ["约束", "储备非负、输出有界、同状态同输入同结果", "审计介质、容灾和升级治理"],
        ], [37 * mm, 68 * mm, 60 * mm], st),
        heading("3.2 执行与结算层：保证结果真正落地", 2, st),
        paragraph(
            "执行层负责保存状态、验证身份与授权、并发控制、原子提交、失败回滚、审计记录和最终结算。它可以采用"
            "权威服务器、许可账本、公开链或混合结构。运行载体改变信任、性能、隐私和治理边界，但不应悄悄改变"
            "Bancor 的数学结果。",
            body,
        ),
        styled_table([
            ["运行载体", "主要优势", "主要代价或信任边界"],
            ["权威服务器与数据库", "高性能、低成本、隐私与权限控制清晰", "依赖运营方、系统密钥和数据库完整性"],
            ["许可账本", "多方共同记账、成员范围可控", "需要成员治理、共识和运维协调"],
            ["公开链", "状态公开、规则可验证、弱化单一运营方", "费用、延迟、抢跑风险和升级治理更复杂"],
            ["混合结构", "高频计算留在服务端，关键承诺外部验证", "必须明确两层状态同步和争议处理规则"],
        ], [42 * mm, 61 * mm, 62 * mm], st),
        heading("3.3 链上实现：一种可选部署方式", 2, st),
        paragraph(
            "只有选择公开链或许可链部署时，才需要讨论链上储备托管、合约原子性、交易费用、区块确认、抢跑与"
            "可提取价值、预言机依赖、合约升级权限和跨链风险。链上实现应逐条证明其状态转换与算法层一致；不能"
            "因为采用链上载体，就把共识、代币标准或某条链的特性写进 Bancor 公式本身。",
            body,
        ),
        heading("3.4 当前 Bancor Plus 的实现选择", 2, st),
        paragraph(
            "当前 Bancor Plus 使用权威服务器、签名授权和原子数据库事务完成结算。这是面向现阶段性能、权限和运维"
            "需求作出的执行层选择，不是对 Bancor 算法的重新定义。未来更换为其他账本时，应保持报价、状态转换、"
            "利润分配与注入控制公式不变，只替换状态托管、授权、提交与审计机制。",
            body,
        ),
        callout(
            "边界原则：算法说明回答“怎么算”；执行层说明回答“谁可以执行、状态存在哪里、如何确认和追责”；"
            "链上章节只讨论选择链作为执行层后新增的问题。",
            st["callout"],
            PALE_CYAN,
        ),

        heading("4. Bancor Plus 的设计范围与独特功能", 1, st),
        paragraph(
            "Bancor Plus 保留储备曲线的可计算兑换，同时增加企业与团队所需的资金形成、利润分配、注入控制和审计观测。"
            "其独特性不在于更换基本交易公式，而在于把交易曲线与一个独立、受约束、可核对的 USD 资金循环组合起来，"
            "再把真实经营利润与团队、用户的可核验贡献连接。",
            body,
        ),
        styled_table([
            ["维度", "原始 Bancor 思想", "Bancor Plus 当前实现"],
            ["流动性来源", "算法读取储备状态", "AIC/USD 储备池 + 独立组织参与资金池"],
            ["价格形成", "储备与 CRR 连续定价", "双储备精确输入曲线，池内边际价为 USD/AIC 储备比"],
            ["额外资金机制", "储备由购买与初始配置形成", "合格 AI 节点首次参与形成预算，控制器再择机注入市场"],
            ["利润与奖励", "不属于原始核心转换公式", "真实经营利润按流动性、团队、用户与留存用途分配"],
            ["注资性质", "不属于原始核心交易动作", "只增加 Bancor USD 储备，不移动 AIC，不生成交易或手续费"],
            ["可观测性", "储备状态与转换记录", "不可变凭证、资产流向、市场版本、注资感知价格 K 线"],
            ["结算边界", "由独立执行层决定", "当前采用权威账本、签名请求和原子数据库事务"],
        ], [29 * mm, 62 * mm, 74 * mm], st),
        Spacer(1, 3 * mm),
        architecture_figure("zh"),
        paragraph("图 2. Bancor Plus 的资金与观测闭环。交易路径和非交易注资路径在账本中严格分离。", st["caption"]),

        heading("5. 交易曲线与手续费", 1, st),
        heading("5.1 精确输入报价", 2, st),
        paragraph(
            "用户给定输入金额 Q，系统先按基点费率 f 计算手续费，曲线输入 q 为扣费后的金额。输出 z 由当前两侧"
            "储备和净输入共同决定；输入越大，沿曲线移动越远，价格影响也越显著。[4]",
            body,
        ),
        formula_box([
            "fee = Q * f / 10,000",
            "q = Q - fee",
            "z = q * Rout / (Rin + q)",
            "price_impact_bps = q * 10,000 / (Rin + q)",
        ], st["formula"]),
        heading("5.2 买入与卖出后的储备", 2, st),
        styled_table([
            ["方向", "用户输入", "用户输出", "储备更新"],
            ["买入 AIC", "Q USD", "z AIC", "USD 储备 + q；AIC 储备 - z"],
            ["卖出 AIC", "Q AIC", "z USD", "AIC 储备 + q；USD 储备 - z"],
        ], [28 * mm, 38 * mm, 38 * mm, 61 * mm], st),
        paragraph(
            "手续费不进入曲线储备，而进入独立手续费账本。卖出还受 USD 储备硬底线与自动暂停阈值约束。报价绑定"
            "市场版本、输入、输出、最低到账、费率、随机数和过期时间；执行前重新报价，若费率变高或最低到账"
            "不满足则拒绝。",
            body,
        ),

        heading("6. 企业与团队的参与资金池", 1, st),
        paragraph(
            "在当前实现中，组织以白名单 AI 节点作为合格参与单元，并将节点身份 H 与资产账户分开。只有节点完成"
            "第一次有效资产账户绑定，且同时具备资产所有者签名和硬件签名时，系统才认定首次参与。每个节点身份"
            "仅在第一次合格绑定时向独立参与资金池形成 100 USD 预算；更换资产账户、重复绑定或重放请求不会重复形成预算。[5]",
            body,
        ),
        paragraph(
            "这笔 USD 不直接记入用户账户，也不立即进入 Bancor 储备。它先形成一个可核对的系统资金池 F，"
            "从而把“企业或团队扩大 AI 参与规模时形成预算”和“市场何时需要更多 USD 深度”拆成两个独立决策。"
            "节点首次参与只是当前实现采用的预算触发器；未来也可由经审计的项目预算或已结算经营利润补充，但不能"
            "把尚未实现的池内价格上涨当作利润。发行记录、"
            "资金池余额和后续转出都写入资产浏览器账本。",
            body,
        ),

        heading("7. 动态单边 USD 注入算法", 1, st),
        heading("7.1 变量与目标", 2, st),
        styled_table([
            ["符号", "含义"],
            ["B", "执行前 Bancor USD 储备"],
            ["F", "组织参与资金池 USD 余额"],
            ["S", "Bancor USD 在 B+F 中的目标占比"],
            ["d", "目标附近不触发注入的平衡缓冲区"],
            ["r_min, r_max", "每轮从资金池余额提取的比例上下限"],
            ["c", "单轮注入相对当前 Bancor USD 储备的上限"],
            ["A", "本轮实际注入 USD"],
        ], [35 * mm, 130 * mm], st),
        heading("7.2 算法", 2, st),
        formula_box([
            "T = (B + F) * S",
            "G = max(T - B, 0)",
            "D = T * d",
            "e = 0,                                      if G <= D",
            "e = min(1, (G - D) / (T - D)),             otherwise",
            "r = r_min + (r_max - r_min) * e",
            "R = F * r",
            "C = B * c",
            "A = min(F, R, G, C)",
        ], st["formula"]),
        paragraph(
            "若资金池为空、B 已达到或超过目标，或缺口处于平衡缓冲区内，则本轮注入为零，但仍可记录决策凭证"
            "并推进调度。",
            body,
        ),
        injection_figure("zh"),
        paragraph("图 3. 当前参数下，缺口严重度从 0 增至 1 时，选定注入比例由 0.1% 线性升至 1%。", st["caption"]),
        heading("7.3 当前策略参数", 2, st),
        styled_table([
            ["参数", "测试值", "作用"],
            ["执行间隔", "600 秒", "首个合格心跳后等待完整间隔；停机恢复最多补做一次"],
            ["最低比例", "0.1%", "缓冲区外的最低资金池提取速度"],
            ["最高比例", "1%", "最大缺口严重度下的提取速度"],
            ["目标占比", "50%", "目标为 Bancor USD 与资金池 USD 大致等量"],
            ["平衡缓冲区", "1%", "抑制目标附近的微小反复操作"],
            ["单次池增幅上限", "2%", "防止单轮注入相对当前储备过大"],
        ], [38 * mm, 32 * mm, 95 * mm], st),
        heading("7.4 注入后的市场状态", 2, st),
        formula_box([
            "F' = F - A",
            "B' = B + A",
            "X' = X                         (AIC reserve unchanged)",
            "p' = (B + A) / X",
            "k' = X * (B + A) > X * B       (when A > 0)",
        ], st["formula"]),
        paragraph(
            "这是直接增加储备，不是买入。它不从 AIC 储备取出资产，也不向任何用户发放 AIC；没有交易 ID、"
            "成交量、交易手续费或用户余额变化。由于 AIC 储备不变而 USD 储备增加，池内 AIC 边际价格上升，"
            "卖出 AIC 时可用的 USD 深度也增加。该经济效果必须与普通双边流动性存入区分。",
            body,
        ),

        heading("8. 利润分配与团队、用户奖励算法", 1, st),
        heading("8.1 先定义可分配利润", 2, st),
        paragraph(
            "Bancor 提供定价、兑换和流动性，不会凭空创造经营利润。利润必须来自已经结算、能够对账的经济活动。"
            "对企业和团队而言，主要来源可以是 AI 推理、训练、模型托管、数据服务、软件订阅和交易手续费。资金池"
            "注入只是资产从一个组织账户移动到另一个储备账户；注入导致的边际价格上升也只是未实现的估值变化，"
            "两者都不能进入可分配利润。",
            body,
        ),
        styled_table([
            ["项目", "是否可进入利润", "处理原则"],
            ["已结算 AI 服务收入", "可以", "扣除直接成本、退款、税费与合同负债后确认"],
            ["已收取交易手续费", "可以", "按组织政策计入收入或风险准备"],
            ["组织参与资金池注入", "不可以", "属于内部资本转移，不是收入"],
            ["储备变化带来的账面升值", "不可以", "未实现收益，不作为奖励来源"],
            ["首次参与形成的预算", "不可以", "先进入独立资金池，只服务于既定预算用途"],
        ], [52 * mm, 35 * mm, 78 * mm], st),
        formula_box([
            "Pi_t = max(R_t - C_t - L_t - V_t, 0)",
            "R_t: settled operating revenue and eligible fees",
            "C_t: verified operating costs",
            "L_t: refunds, taxes, and contractual liabilities",
            "V_t: required risk-reserve top-up",
        ], st["formula"]),
        paragraph(
            "只有 Pi_t 大于零时才进入奖励瀑布。亏损期不通过增发奖励或抽取 Bancor 储备伪造利润；未弥补亏损和"
            "准备金缺口应结转到下一结算周期。",
            body,
        ),
        heading("8.2 自适应利润瀑布", 2, st),
        paragraph(
            "每个结算周期先观察 Bancor USD 储备相对目标的缺口，以此决定利润中用于增强流动性的比例 alpha_t。"
            "缺口越大，alpha_t 越接近上限；市场健康时则回到下限。流动性份额先进入组织参与资金池，再由第 7 节"
            "控制器择机注入，而不是绕过限额直接进入 Bancor。剩余利润按治理权重分给团队、用户和留存收益。",
            body,
        ),
        formula_box([
            "h_t = clamp((T - B) / T, 0, 1)",
            "alpha_t = alpha_min + (alpha_max - alpha_min) * h_t",
            "Z = w_team + w_user + w_retain",
            "Liquidity_t = alpha_t * Pi_t",
            "Team_t = (1 - alpha_t) * w_team / Z * Pi_t",
            "User_t = (1 - alpha_t) * w_user / Z * Pi_t",
            "Retained_t = (1 - alpha_t) * w_retain / Z * Pi_t",
        ], st["formula"]),
        paragraph(
            "alpha 的上下限、三类治理权重和单期支付上限必须在周期开始前公布并版本化。这样既能在流动性不足时"
            "优先增强退出能力，也能防止管理者在看到分配结果后临时改变团队或用户份额。",
            body,
        ),
        heading("8.3 团队与用户的个体分配", 2, st),
        paragraph(
            "团队奖励不应只按工时或持币量分配，而应使用可核验的交付、质量、可靠性、知识复用和协作贡献。"
            "用户奖励可采用已结算使用价值、有效反馈、长期留存和生态贡献，但应排除自成交、刷量、退款订单和"
            "无法验证的邀请。平方根变换可以降低单一大贡献者对当期奖励的垄断，同时保留正向激励。",
            body,
        ),
        formula_box([
            "s_i = max(weighted_verified_contribution_i - penalties_i, 0)",
            "a_i = sqrt(s_i)",
            "team_reward_i = Team_t * a_i / sum(a_j)",
            "u_k = sqrt(max(verified_user_value_k - penalties_k, 0))",
            "user_reward_k = User_t * u_k / sum(u_m)",
        ], st["formula"]),
        heading("8.4 奖励交付与 Bancor 曲线的关系", 2, st),
        styled_table([
            ["交付方式", "对 Bancor 的影响", "适用场景"],
            ["从奖励金库转出 AIC", "不触发曲线交易；减少组织 AIC 库存", "团队与用户直接获得内部奖励资产"],
            ["直接支付 USD", "不触发曲线交易；减少利润现金", "用户需要稳定记账单位时"],
            ["用利润回购 AIC 后分配", "形成真实买入、手续费和价格影响", "希望奖励与市场需求同步时"],
        ], [50 * mm, 61 * mm, 54 * mm], st),
        paragraph(
            "若采用回购后奖励，应使用版本化报价，将单次回购限制在 Bancor USD 储备的一定比例和最大价格影响内，"
            "并跨多个时间窗执行。回购记录、获得的 AIC、团队和用户收款明细必须能从利润凭证追溯；任何未完成回购"
            "只能退回利润待分配账户，不能被记成已经发放的奖励。",
            body,
        ),
        callout(
            "推荐流程：先核算真实利润，再确定流动性、团队、用户和留存份额；最后选择不经过曲线或经过受限回购的"
            "交付路径。利润核算、流动性注入和奖励发放是三个相互关联但必须分账的动作。",
            st["callout"],
            PALE_CYAN,
        ),

        heading("9. 稳定性与收敛性质", 1, st),
        paragraph(
            "在没有交易、没有新增合格参与预算且只发生 F 到 B 的内部转移时，B+F 保持不变，因此目标 T 也保持不变。"
            "每次正注入都会使缺口 G 恰好减少 A。只要资金池仍有余额且缺口在缓冲区外，"
            "序列会单调接近目标。比例上限抑制资金池快速耗尽，单次池增幅上限约束相对市场冲击，缓冲区阻止目标附近"
            "出现高频微调。",
            body,
        ),
        formula_box([
            "B_next = B + A",
            "F_next = F - A",
            "T_next = (B_next + F_next) * S = T",
            "G_next = max(G - A, 0)",
        ], st["formula"]),
        paragraph(
            "该控制器是单向的：它可以把 USD 从资金池注入 Bancor，却不会在储备高于目标时自动抽回。因交易造成的"
            "超目标状态只会暂停新注入。因此，它保证的是有界、可审计的补充路径，而不是双向锚定，也不保证固定价格。",
            body,
        ),

        heading("10. 数值案例：测试数据快照", 1, st),
        heading("10.1 测试储备与注入计算", 2, st),
        paragraph(
            "本文测试数据快照采用以下状态：AIC 储备 X = "
            "155,725,642.07，Bancor USD 储备 B = 36,573.93，激活资金池 F = "
            "94,509.59，边际价格约为 0.00023486 USD/AIC，交易费率为 50 个基点。[7]",
            body,
        ),
        styled_table([
            ["计算量", "结果"],
            ["目标储备 T", "65,541.76 USD"],
            ["目标缺口 G", "28,967.83 USD"],
            ["平衡缓冲金额 D", "655.42 USD"],
            ["缺口严重度 e", "0.4363"],
            ["选定比例 r", "0.4927%"],
            ["按比例金额 R", "465.65 USD"],
            ["单次池增幅上限 C", "731.48 USD"],
            ["实际注入 A", "465.65 USD"],
            ["注入后边际价格", "约 0.00023785 USD/AIC（上升约 1.2731%）"],
        ], [65 * mm, 100 * mm], st),
        paragraph(
            "同一测试数据快照下，若输入 100 USD 买入 AIC，50 个基点手续费为 0.50 USD，"
            "净曲线输入为 99.50 USD，预期输出约 422,504.82 AIC。该例展示交易公式；实际执行仍需"
            "通过版本化报价、最低到账和签名校验。",
            body,
        ),
        heading("10.2 企业利润分配示例", 2, st),
        paragraph(
            "以下为说明性结算周期，不代表线上实际收入或既定分配政策。假设企业已结算 AI 业务收入与合格手续费"
            "合计 120,000 USD，核验成本 60,000 USD，退款、税费与合同负债 10,000 USD，风险准备补足 5,000 USD，"
            "则可分配利润 Pi_t 为 45,000 USD。若利润流动性比例下限为 10%、上限为 30%，按当前储备缺口得到"
            "h_t = 0.4420、alpha_t = 18.8395%；剩余治理权重采用团队 5、用户 3、留存 2。",
            body,
        ),
        styled_table([
            ["用途", "金额", "后续处理"],
            ["流动性份额", "8,477.78 USD", "进入组织参与资金池，仍由动态控制器限速注入"],
            ["团队奖励池", "18,261.11 USD", "按经平方根调整的团队贡献分数分配"],
            ["用户奖励池", "10,956.67 USD", "按可核验用户价值分数分配"],
            ["留存收益", "7,304.44 USD", "保留在组织利润账户，用于后续经营与风险"],
            ["合计", "45,000.00 USD", "与可分配利润完全对账"],
        ], [48 * mm, 38 * mm, 79 * mm], st),
        paragraph(
            "这一步只确定用途，不等于奖励已经支付。团队与用户池还要生成收款人明细；若选择回购 AIC 后奖励，"
            "必须按第 8.4 节执行受限交易，并以最终获得的 AIC 数量完成分配凭证。",
            body,
        ),

        heading("11. 审计、价格 K 线与安全边界", 1, st),
        heading("11.1 非交易注资的独立可观测性", 2, st),
        paragraph(
            "每次注资在一个数据库事务内完成资金池扣减、Bancor USD 储备增加、市场版本更新、不可变注资凭证、"
            "资产账本和浏览器流向写入。任何一步失败则全部回滚。注资事件进入“池子边际价格”K 线，使无成交但"
            "储备发生变化的时间窗仍能反映真实价格状态；但其注资次数和 USD 金额独立展示，不计入成交笔数、"
            "AIC/USD 成交量或手续费。[6]",
            body,
        ),
        heading("11.2 防护措施", 2, st),
        bullets([
            "卖出受 USD 储备硬底线和自动暂停阈值约束，避免继续耗尽储备。",
            "报价与市场版本绑定；执行时重算，防止旧报价跨状态生效。",
            "交易签名绑定方向、金额、费率、最低到账、随机数、任务和过期时间。",
            "账户、市场、账本、手续费和交易记录在一个立即事务中更新。",
            "注资凭证和资产流水不可修改，并通过离线对账验证总量与状态变化。",
        ], body),
        heading("11.3 仍然存在的限制", 2, st),
        bullets([
            "当前部署的数据库、系统密钥和结算服务仍是关键控制点；这是执行层风险，不是储备曲线公式本身的风险。",
            "内部 USD 不代表银行存款或法币赎回权；AIC 价格也不存在保本或稳定承诺。",
            "单边注入会抬高池内边际价格并改变曲线常数，属于有经济影响的政策动作。",
            "控制器只注入不抽回；当外部交易把储备推至目标以上时，它只能停止新增注入。",
            "目标、比例和上限是政策参数，不是从市场风险中自动推导出的最优值，需要压力测试与治理。",
            "当前单一权威 Core 与数据库提供原子一致性，但在跨区域容灾和多写者高可用方面仍需后续架构演进。",
        ], body),

        heading("12. 结论", 1, st),
        paragraph(
            "Bancor 的关键贡献，是把流动性从“等待对手方”转化为“面对储备与公式”。Bancor Plus 将这一思想用于"
            "AI 时代的企业与团队：合格参与形成独立预算，动态算法根据 Bancor USD 储备与资金池之间的目标关系"
            "选择注入比例，再以目标缺口和单次池增幅双重限幅；真实经营利润则通过独立瀑布分给流动性、团队、用户"
            "和留存收益。交易、注资与奖励在会计、市场统计和审计上保持分离。",
            body,
        ),
        paragraph(
            "储备公式、注入控制和利润分配属于算法层；身份、托管、提交、确认和审计属于执行层，两者应分别验证。"
            "这一设计的价值不在于宣称消除波动，而在于让组织把 AI 业务收入、内部奖励和退出流动性纳入同一套"
            "可计算、可配置、可回滚、可审计的规则。其后续研究重点应包括利润确认政策、贡献评分抗操纵性、"
            "极端卖压下的资金寿命、双向再平衡是否必要、治理权限、多节点一致性与公开验证机制。",
            body,
        ),

        references_heading("参考文献", st),
    ]
    refs = [
        "[1] E. Hertzog, G. Benartzi, and G. Benartzi. Bancor Protocol: Continuous Liquidity and Asynchronous Price Discovery for Tokens through their Smart Contracts. Draft 0.77, 2017. https://resources.bancor.network/pages/BancorProtocolWhitepaper.pdf",
        "[2] G. Angeris and T. Chitra. Improved Price Oracles: Constant Function Market Makers. Proceedings of AFT 2020. https://arxiv.org/abs/2003.10001",
        "[3] G. Angeris, A. Agrawal, A. Evans, T. Chitra, and S. Boyd. Constant Function Market Makers: Multi-Asset Trades via Convex Optimization. 2021. https://arxiv.org/abs/2107.12484",
        "[4] NNI implementation reference. nni_server/bancor_math.mjs and nni_server/storage.mjs, commit f21375395e0204eec7f42f6c54af9a9bd5c16210, reviewed 2026-09-28.",
        "[5] NNI implementation reference. nni_server/activation_fund.mjs, one-time 100 USD qualified-participation budget policy, reviewed 2026-09-28.",
        "[6] NNI implementation reference. nni_server/activation_fund_liquidity.mjs, activation_fund_liquidity_config.mjs, and pool-price candle projections, commit f21375395e0204eec7f42f6c54af9a9bd5c16210.",
        "[7] Test-data source endpoint. https://api-1.matrixai.one/v1/nni/server/bancor/market, accessed 2026-09-28 08:30:31 CST.",
    ]
    story.extend(Paragraph(escape(ref), st["reference"]) for ref in refs)
    story += [
        Spacer(1, 2 * mm),
        Paragraph(
            "复现说明：本文所有 Bancor Plus 数值均由当前公式重算；测试数据快照仅用于说明，不构成收益预测、"
            "估值意见或交易建议。",
            st["reference"],
        ),
    ]
    return story


def section_en(st: dict[str, ParagraphStyle]) -> list:
    body = st["body"]
    story = []
    story += [
        heading("1. Introduction", 1, st),
        paragraph(
            "The core liquidity problem is not whether an asset can be recorded, but whether a holder can obtain a predictable conversion "
            "when no opposite order appears at the same time. An order book depends on buyers and sellers meeting in price and time. A "
            "reserve-curve market instead lets a trader face asset reserves and a public state-transition formula. The mechanism does not "
            "remove risk; it makes part of liquidity provision computable and verifiable.",
            body,
        ),
        paragraph(
            "Enterprises and teams in the AI era face two linked problems: converting compute, models, data, delivery, and user participation "
            "into internal rewards, and giving those rewards continuous and explainable liquidity. Bancor Plus preserves reserve-driven conversion, "
            "then adds participation funding, profit distribution, injection control, and audit observability. It is not a general-purpose exchange, "
            "stablecoin, fiat gateway, or any particular chain or ledger. It is an organizational settlement and incentive algorithm with explicit boundaries.",
            body,
        ),
        callout(
            "Research question: when enterprises and teams continuously issue AI-contribution rewards, how can they preserve exit liquidity and "
            "reward team members and users from real profit without fabricating trades, misclassifying capital funding, or allowing unbounded support?",
            st["callout"],
        ),

        heading("2. Origin and Core Ideas of Bancor", 1, st),
        heading("2.1 Name and Motivation", 2, st),
        paragraph(
            "The name Bancor honors John Maynard Keynes's wartime proposal for a supranational clearing currency. The original Bancor paper "
            "borrowed the name for a different problem: liquidity and conversion among digital tokens. It framed the double coincidence of "
            "wants as a barrier for long-tail currencies and proposed smart tokens whose prices are continuously computed from reserve state. "
            "Smart contracts were an early execution medium, not a prerequisite of the formulas.[1]",
            body,
        ),
        heading("2.2 Constant Reserve Ratio and Continuous Pricing", 2, st),
        paragraph(
            "The original model expresses instantaneous price using reserve balance R, smart-token supply S, and a constant reserve ratio. "
            "The price is recomputed after each purchase or liquidation, so price discovery unfolds asynchronously rather than requiring a "
            "matched bid and ask.[1]",
            body,
        ),
        formula_box([
            "P = R / (S * CRR)",
            "Purchase: DeltaS = S * ((1 + DeltaR / R)^CRR - 1)",
            "Liquidation: DeltaR = R * (1 - (1 - DeltaS / S)^(1 / CRR))",
        ], st["formula"]),
        paragraph(
            "Effective execution integrates across infinitesimal state changes. A larger trade therefore moves farther along the curve and "
            "incurs more slippage, while deeper reserves reduce the movement produced by the same trade size.",
            body,
        ),
        heading("2.3 Two-Reserve Conversion", 2, st),
        paragraph(
            "A converter that holds two reserve assets can be viewed as entering an intermediate supply and exiting the other reserve. In "
            "the symmetric two-reserve case, the exact-input transformation has a compact direct form. For input reserve Rin, output reserve "
            "Rout, net input q, and output z:",
            body,
        ),
        formula_box([
            "z = q * Rout / (Rin + q)",
            "(Rin + q) * (Rout - z) = Rin * Rout",
            "p_marginal = R_USD / R_AIC",
        ], st["formula"]),
        paragraph(
            "This transformation preserves the reserve product and is a two-asset constant-function market. "
            "Modern CFMM research formalizes these mechanisms through reserve-dependent trading functions and studies their pricing, "
            "reserve bounds, and path properties.[2][3]",
            body,
        ),
        reserve_curve_figure("en"),
        paragraph("Figure 1. Normalized exact-input curve. Output keeps increasing, but marginal output declines with trade size.", st["caption"]),

        heading("3. Separating the Bancor Algorithm from Its Execution Medium", 1, st),
        heading("3.1 Algorithm Layer: State Transitions Only", 2, st),
        paragraph(
            "Bancor is first a reserve-pricing and state-transition algorithm. It reads reserve balances, supply or paired-reserve state, "
            "policy parameters, and a conversion input; it then computes a quote, output, price impact, and next state. Given the same state, "
            "parameters, and input, it should produce the same result. This definition is independent of whether the state is held in a "
            "database, smart contract, blockchain, or another ledger.",
            body,
        ),
        styled_table([
            ["Algorithm element", "Content", "Outside its scope"],
            ["State", "Reserve balances, supply, fees, and control parameters", "Where state is stored and who custodies it"],
            ["Input", "Direction, amount, and minimum-output constraints", "Identity, authentication, and authorization"],
            ["Computation", "Continuous price, output, impact, and next reserves", "Signature format, confirmation, and commit protocol"],
            ["Constraints", "Nonnegative reserves, bounded output, deterministic result", "Audit medium, disaster recovery, and upgrade governance"],
        ], [37 * mm, 68 * mm, 60 * mm], st),
        heading("3.2 Execution and Settlement Layer", 2, st),
        paragraph(
            "The execution layer turns an algorithmic result into an authoritative state change. It is responsible for custody, identity and "
            "permission checks, concurrency control, atomic commit, rollback, durable storage, receipts, audit, and final settlement. Different "
            "organizations may choose different carriers without changing the Bancor formulas.",
            body,
        ),
        styled_table([
            ["Execution medium", "Primary strengths", "Costs and trust boundary"],
            ["Authoritative server and database", "Low latency, mature transactions, controlled recovery", "Operator controls service, keys, and database"],
            ["Permissioned ledger", "Shared governance among known parties", "Membership, consensus, and operations remain governed"],
            ["Public chain", "Public state verification and composability", "Fees, confirmation delay, public ordering, and contract risk"],
            ["Hybrid", "Private execution with selected proofs or settlement published externally", "Requires explicit reconciliation and finality rules"],
        ], [42 * mm, 61 * mm, 62 * mm], st),
        heading("3.3 On-Chain Implementation: One Optional Deployment", 2, st),
        paragraph(
            "When Bancor is implemented on a blockchain, the design must additionally address contract custody, transaction fees, confirmation "
            "and reorganization rules, public transaction ordering, front-running or extractable value, oracle dependencies, contract upgrades, "
            "and cross-chain risk. These are properties of the chosen on-chain execution environment. They must be analyzed separately rather "
            "than written into the definition of the reserve algorithm itself.",
            body,
        ),
        heading("3.4 Current Bancor Plus Implementation Choice", 2, st),
        paragraph(
            "The current Bancor Plus system uses an authoritative service, signed authorization, and atomic database transactions. This is an "
            "execution-layer choice, not a claim that Bancor requires centralized settlement. A future permissioned-ledger, public-chain, or "
            "hybrid carrier can preserve the same quote, funding-control, and profit-allocation algorithms if their state transitions and "
            "invariants remain equivalent.",
            body,
        ),
        callout(
            "Boundary rule: the algorithm explains how to calculate; the execution layer explains who may execute, where state lives, and how "
            "results are confirmed and audited. On-chain analysis applies only after a blockchain has been chosen as the execution medium.",
            st["callout"],
            PALE_CYAN,
        ),

        heading("4. Scope and Distinctive Features of Bancor Plus", 1, st),
        paragraph(
            "Bancor Plus retains computable reserve-curve exchange while adding the funding, profit-distribution, control, and observation layers "
            "needed by enterprises and teams. Its distinctive contribution is not a replacement of the base trading equation, but a strictly "
            "accounted USD funding cycle connected to verifiable team and user contributions.",
            body,
        ),
        styled_table([
            ["Dimension", "Original Bancor idea", "Current Bancor Plus implementation"],
            ["Liquidity source", "Algorithm reads reserve state", "AIC/USD reserves plus a separate participation fund"],
            ["Price formation", "Reserve and CRR-based continuous pricing", "Two-reserve exact-input curve; marginal price equals USD/AIC reserve ratio"],
            ["Additional funding", "Initial reserves and purchase flows", "First qualified AI-node participation forms budget; a controller later injects it"],
            ["Profit and rewards", "Outside the original conversion formula", "Real operating profit is allocated to liquidity, teams, users, and retained earnings"],
            ["Injection semantics", "Not a core conversion action", "Adds only USD reserve; moves no AIC and creates no trade or fee"],
            ["Observability", "Conversion and reserve state", "Immutable receipts, asset flows, market versions, and funding-aware price candles"],
            ["Settlement boundary", "Defined by a separate execution layer", "Current implementation uses an authoritative ledger, signed requests, and atomic database transactions"],
        ], [29 * mm, 62 * mm, 74 * mm], st),
        Spacer(1, 3 * mm),
        architecture_figure("en"),
        paragraph("Figure 2. Bancor Plus funding and observation loop. Trade and non-trade funding paths remain separate in the ledger.", st["caption"]),

        heading("5. Trading Curve and Fees", 1, st),
        heading("5.1 Exact-Input Quote", 2, st),
        paragraph(
            "For gross input Q and fee rate f in basis points, the curve receives the net amount q after fees. Output z depends on the two "
            "current reserves and the net input. Larger inputs move farther along the curve and create greater price impact.[4]",
            body,
        ),
        formula_box([
            "fee = Q * f / 10,000",
            "q = Q - fee",
            "z = q * Rout / (Rin + q)",
            "price_impact_bps = q * 10,000 / (Rin + q)",
        ], st["formula"]),
        heading("5.2 Reserve Updates", 2, st),
        styled_table([
            ["Direction", "User input", "User output", "Reserve transition"],
            ["Buy AIC", "Q USD", "z AIC", "USD reserve + q; AIC reserve - z"],
            ["Sell AIC", "Q AIC", "z USD", "AIC reserve + q; USD reserve - z"],
        ], [28 * mm, 38 * mm, 38 * mm, 61 * mm], st),
        paragraph(
            "Fees are recorded outside curve reserves. A sell is additionally constrained by a hard USD reserve floor and an automatic pause "
            "threshold. Each quote binds the market version, input, output, minimum output, fee, nonce, and expiry. Execution recalculates the "
            "quote and rejects a higher fee or insufficient output.",
            body,
        ),

        heading("6. Participation Fund for Enterprises and Teams", 1, st),
        paragraph(
            "In the current implementation, an organization treats an allowlisted AI node as a qualified participation unit and separates node "
            "identity H from its asset account. First participation is accepted only after a valid asset-account binding with both owner and hardware "
            "signatures. Each node identity forms a 100 USD budget in a separate participation fund only once. Rebinding, account replacement, and "
            "replay do not form budget again.[5]",
            body,
        ),
        paragraph(
            "This USD does not enter the user's account and does not immediately enter Bancor reserves. It first forms an auditable fund F, separating "
            "budget formation as enterprise or team AI participation expands from the decision of when the market needs more USD depth. Node "
            "participation is the current implementation trigger; audited project budgets or settled operating profit could later replenish the fund, "
            "but unrealized pool appreciation must never be classified as profit. Budget formation and subsequent transfers appear in the asset ledger.",
            body,
        ),

        heading("7. Adaptive One-Sided USD Injection", 1, st),
        heading("7.1 Variables and Target", 2, st),
        styled_table([
            ["Symbol", "Meaning"],
            ["B", "Bancor USD reserve before the step"],
            ["F", "USD balance of the organizational participation fund"],
            ["S", "Target share of Bancor USD within B+F"],
            ["d", "Balance buffer around the target"],
            ["r_min, r_max", "Lower and upper fractions of F selectable per step"],
            ["c", "Per-step cap relative to the current Bancor USD reserve"],
            ["A", "Actual USD reserve addition"],
        ], [35 * mm, 130 * mm], st),
        heading("7.2 Algorithm", 2, st),
        formula_box([
            "T = (B + F) * S",
            "G = max(T - B, 0)",
            "D = T * d",
            "e = 0,                                      if G <= D",
            "e = min(1, (G - D) / (T - D)),             otherwise",
            "r = r_min + (r_max - r_min) * e",
            "R = F * r",
            "C = B * c",
            "A = min(F, R, G, C)",
        ], st["formula"]),
        paragraph(
            "If the fund is empty, B is at or above target, or the gap lies inside the balance buffer, the step transfers zero while still "
            "allowing a decision receipt and the schedule to advance.",
            body,
        ),
        injection_figure("en"),
        paragraph("Figure 3. Under the current policy, the selected rate rises linearly from 0.1% to 1% as gap severity moves from 0 to 1.", st["caption"]),
        heading("7.3 Current Policy", 2, st),
        styled_table([
            ["Parameter", "Test value", "Purpose"],
            ["Interval", "600 seconds", "Wait one full interval after the first eligible heartbeat; catch up at most once"],
            ["Minimum rate", "0.1%", "Slowest extraction from F outside the buffer"],
            ["Maximum rate", "1%", "Extraction rate at maximum gap severity"],
            ["Target share", "50%", "Targets roughly equal USD balances in Bancor and the participation fund"],
            ["Balance buffer", "1%", "Suppresses small adjustments near target"],
            ["Pool step cap", "2%", "Limits one addition relative to current Bancor USD reserve"],
        ], [38 * mm, 32 * mm, 95 * mm], st),
        heading("7.4 Market State After Funding", 2, st),
        formula_box([
            "F' = F - A",
            "B' = B + A",
            "X' = X                         (AIC reserve unchanged)",
            "p' = (B + A) / X",
            "k' = X * (B + A) > X * B       (when A > 0)",
        ], st["formula"]),
        paragraph(
            "This is direct reserve funding, not a buy. It removes no AIC from the reserve and credits no user with AIC. It creates no trade "
            "identifier, trading volume, fee, or user-balance change. Because AIC reserve stays fixed while USD reserve grows, the marginal "
            "AIC price and available USD sell-side depth both increase. This economic effect differs from a neutral two-sided liquidity deposit.",
            body,
        ),

        heading("8. Profit Distribution and Team/User Rewards", 1, st),
        heading("8.1 Define Distributable Profit First", 2, st),
        paragraph(
            "Bancor supplies pricing, conversion, and liquidity; it does not manufacture operating profit. Profit must come from settled, "
            "reconcilable economic activity. For enterprises and teams, eligible sources may include AI inference, training, model hosting, "
            "data services, software subscriptions, and collected trading fees. A participation-fund transfer is an internal capital movement, "
            "not revenue. A higher marginal price after funding is unrealized valuation change, not distributable profit.",
            body,
        ),
        styled_table([
            ["Item", "Profit eligible?", "Treatment"],
            ["Settled AI-service revenue", "Yes", "Recognize after direct costs, refunds, taxes, and contract liabilities"],
            ["Collected trading fees", "Yes", "Book as revenue or risk reserve under published policy"],
            ["Participation-fund transfer", "No", "Internal capital movement, not income"],
            ["Reserve appreciation", "No", "Unrealized value change, not a reward source"],
            ["First-participation budget", "No", "Restricted budget held for its stated organizational purpose"],
        ], [52 * mm, 35 * mm, 78 * mm], st),
        formula_box([
            "Pi_t = max(R_t - C_t - L_t - V_t, 0)",
            "R_t: settled operating revenue and eligible fees",
            "C_t: verified operating costs",
            "L_t: refunds, taxes, and contractual liabilities",
            "V_t: required risk-reserve top-up",
        ], st["formula"]),
        paragraph(
            "Only a positive Pi_t enters the reward waterfall. A loss period must not mint rewards or drain Bancor reserves to simulate profit; "
            "unrecovered losses and reserve deficiencies carry into the next settlement epoch.",
            body,
        ),
        heading("8.2 Adaptive Profit Waterfall", 2, st),
        paragraph(
            "Each settlement epoch first measures the Bancor USD reserve gap and selects alpha_t, the fraction of profit assigned to liquidity. "
            "A larger gap moves alpha_t toward its ceiling; a healthy market returns it toward its floor. This share enters the participation "
            "fund and remains subject to the controller in Section 7 rather than bypassing injection limits. The remaining profit is allocated "
            "to teams, users, and retained earnings through published governance weights.",
            body,
        ),
        formula_box([
            "h_t = clamp((T - B) / T, 0, 1)",
            "alpha_t = alpha_min + (alpha_max - alpha_min) * h_t",
            "Z = w_team + w_user + w_retain",
            "Liquidity_t = alpha_t * Pi_t",
            "Team_t = (1 - alpha_t) * w_team / Z * Pi_t",
            "User_t = (1 - alpha_t) * w_user / Z * Pi_t",
            "Retained_t = (1 - alpha_t) * w_retain / Z * Pi_t",
        ], st["formula"]),
        paragraph(
            "The alpha bounds, governance weights, and per-epoch payout cap must be published and versioned before the epoch begins. This favors "
            "exit liquidity during stress while preventing managers from changing team or user shares after seeing the result.",
            body,
        ),
        heading("8.3 Allocation Within Team and User Pools", 2, st),
        paragraph(
            "Team rewards should reflect verifiable delivery, quality, reliability, reusable knowledge, and collaboration rather than hours or "
            "holdings alone. User rewards may reflect settled usage value, useful feedback, retention, and ecosystem contribution, while excluding "
            "self-trading, artificial volume, refunded orders, and unverifiable referrals. A square-root transform limits dominance by a single "
            "large contributor while preserving positive incentives.",
            body,
        ),
        formula_box([
            "s_i = max(weighted_verified_contribution_i - penalties_i, 0)",
            "a_i = sqrt(s_i)",
            "team_reward_i = Team_t * a_i / sum(a_j)",
            "u_k = sqrt(max(verified_user_value_k - penalties_k, 0))",
            "user_reward_k = User_t * u_k / sum(u_m)",
        ], st["formula"]),
        heading("8.4 Delivery Choices and Their Curve Effects", 2, st),
        styled_table([
            ["Delivery", "Bancor effect", "Use case"],
            ["Transfer treasury AIC", "No curve trade; organizational AIC inventory falls", "Direct internal-asset rewards"],
            ["Pay USD", "No curve trade; distributable cash falls", "Users need a stable accounting unit"],
            ["Buy AIC and distribute", "Real buy, fee, and price impact", "Rewards should coincide with market demand"],
        ], [50 * mm, 61 * mm, 54 * mm], st),
        paragraph(
            "A buyback-and-distribute policy should use versioned quotes, cap each buy relative to Bancor USD reserves and maximum price impact, "
            "and execute across multiple windows. The profit receipt must trace to acquired AIC and final team/user recipients. An incomplete "
            "buyback returns to the pending-profit account and cannot be reported as a paid reward.",
            body,
        ),
        callout(
            "Recommended sequence: recognize real profit; allocate liquidity, team, user, and retained shares; then choose a direct payout or "
            "controlled buyback path. Profit recognition, liquidity funding, and reward delivery are linked but separately accounted actions.",
            st["callout"],
            PALE_CYAN,
        ),

        heading("9. Stability and Convergence", 1, st),
        paragraph(
            "With no trades, no newly formed qualified-participation budget, and only internal F-to-B transfers, B+F remains constant, so target T is constant. Every "
            "positive transfer reduces gap G by exactly A. As long as the fund remains nonzero and the gap is outside the buffer, the sequence "
            "approaches the target monotonically. The rate ceiling slows fund depletion, the pool cap "
            "bounds relative market movement, and the balance buffer suppresses micro-adjustments near target.",
            body,
        ),
        formula_box([
            "B_next = B + A",
            "F_next = F - A",
            "T_next = (B_next + F_next) * S = T",
            "G_next = max(G - A, 0)",
        ], st["formula"]),
        paragraph(
            "The controller is one-way: it can move USD into Bancor but does not withdraw reserves when B exceeds target. An above-target state "
            "caused by trading only pauses new funding. The controller therefore supplies a bounded and auditable replenishment path, not a "
            "two-way peg or a fixed-price guarantee.",
            body,
        ),

        heading("10. Numerical Case: Test-Data Snapshot", 1, st),
        heading("10.1 Test Reserves and Funding Step", 2, st),
        paragraph(
            "The test-data snapshot uses AIC reserve X = "
            "155,725,642.07, Bancor USD reserve B = 36,573.93, activation-fund balance F = "
            "94,509.59, marginal price near 0.00023486 USD/AIC, and a 50 basis-point fee.[7]",
            body,
        ),
        styled_table([
            ["Quantity", "Result"],
            ["Target reserve T", "65,541.76 USD"],
            ["Target gap G", "28,967.83 USD"],
            ["Buffer amount D", "655.42 USD"],
            ["Gap severity e", "0.4363"],
            ["Selected rate r", "0.4927%"],
            ["Rate amount R", "465.65 USD"],
            ["Pool step cap C", "731.48 USD"],
            ["Actual addition A", "465.65 USD"],
            ["Post-funding marginal price", "about 0.00023785 USD/AIC, up about 1.2731%"],
        ], [65 * mm, 100 * mm], st),
        paragraph(
            "In the same test-data snapshot, a gross 100 USD AIC purchase pays a 0.50 USD fee, sends 99.50 USD into the curve, "
            "and quotes approximately 422,504.82 AIC. Actual execution still requires the versioned quote, minimum-output check, and "
            "valid signature.",
            body,
        ),
        heading("10.2 Enterprise Profit-Distribution Example", 2, st),
        paragraph(
            "The following illustrative epoch is neither live revenue nor an adopted allocation policy. Suppose settled AI-business revenue "
            "and eligible fees total 120,000 USD, verified costs are 60,000 USD, refunds, taxes, and contract liabilities are 10,000 USD, and "
            "the risk-reserve top-up is 5,000 USD. Distributable profit Pi_t is 45,000 USD. With profit-liquidity bounds of 10% and 30%, the current "
            "reserve gap gives h_t = 0.4420 and alpha_t = 18.8395%. Remaining governance weights are team 5, user 3, and retained 2.",
            body,
        ),
        styled_table([
            ["Purpose", "Amount", "Next action"],
            ["Liquidity share", "8,477.78 USD", "Enter the participation fund; controller still limits injection"],
            ["Team reward pool", "18,261.11 USD", "Allocate by square-root-adjusted team contribution scores"],
            ["User reward pool", "10,956.67 USD", "Allocate by verifiable user-value scores"],
            ["Retained earnings", "7,304.44 USD", "Keep for future operations and risk"],
            ["Total", "45,000.00 USD", "Fully reconciles to distributable profit"],
        ], [48 * mm, 38 * mm, 79 * mm], st),
        paragraph(
            "This step assigns purposes; it does not prove payment. Team and user pools still require recipient-level records. If rewards use an "
            "AIC buyback, Section 8.4's controlled execution applies and the final AIC received must reconcile to distribution receipts.",
            body,
        ),

        heading("11. Auditability, Price Candles, and Safety Boundaries", 1, st),
        heading("11.1 Separate Observation of Non-Trade Funding", 2, st),
        paragraph(
            "Each funding step atomically commits the fund debit, Bancor USD reserve increase, market-version update, immutable funding receipt, "
            "asset ledger, and explorer flow. Any failure rolls back the entire step. Funding events enter pool-marginal-price candles so an "
            "interval with no trade but a changed reserve still shows the real price state. Funding count and USD amount remain separate and do "
            "not enter trade count, AIC/USD volume, or fee totals.[6]",
            body,
        ),
        heading("11.2 Controls", 2, st),
        bullets([
            "Sells are constrained by a hard USD floor and an automatic pause threshold.",
            "Quotes bind a market version and are recalculated at execution.",
            "Signatures bind direction, amount, fee, minimum output, nonce, task, and expiry.",
            "Account, market, ledger, fee, and trade rows update in one immediate transaction.",
            "Funding receipts and asset flows are immutable and subject to offline reconciliation.",
        ], body),
        heading("11.3 Remaining Limitations", 2, st),
        bullets([
            "The current database, system keys, and settlement service remain critical control points; this is execution-layer risk, not reserve-curve formula risk.",
            "Internal USD is neither a bank deposit nor a fiat redemption right; AIC carries no capital or price-stability guarantee.",
            "One-sided funding raises marginal price and changes the curve invariant, so it is an economically consequential policy action.",
            "The controller injects but does not withdraw. It can only stop when external trades move reserves above target.",
            "Targets, rates, and caps are governance parameters rather than automatically optimal risk estimates; they require stress testing.",
            "A single authoritative Core and database provide atomic consistency but still require future work for multi-writer and regional failover.",
        ], body),

        heading("12. Conclusion", 1, st),
        paragraph(
            "Bancor's central contribution was to turn liquidity from waiting for a counterparty into interacting with reserves and a formula. "
            "Bancor Plus applies that idea to enterprises and teams in the AI era. Qualified participation forms separate budget; the adaptive "
            "algorithm selects a funding rate from the reserve gap and constrains each transfer. Real operating profit then follows a separate "
            "waterfall into liquidity, team, user, and retained shares. Trade, funding, and rewards remain distinct in accounting and audit.",
            body,
        ),
        paragraph(
            "The design should not be evaluated as a promise to eliminate volatility. Its value is a computable, configurable, rollback-safe, "
            "and auditable way to connect AI-business revenue, internal rewards, and exit liquidity. Future work should study profit-recognition "
            "policy, manipulation resistance of contribution scores, fund lifetime under extreme selling, two-way rebalancing, governance, "
            "multi-node consistency, and public verification.",
            body,
        ),
        PageBreak(),
        references_heading("References", st),
    ]
    refs = [
        "[1] E. Hertzog, G. Benartzi, and G. Benartzi. Bancor Protocol: Continuous Liquidity and Asynchronous Price Discovery for Tokens through their Smart Contracts. Draft 0.77, 2017. https://resources.bancor.network/pages/BancorProtocolWhitepaper.pdf",
        "[2] G. Angeris and T. Chitra. Improved Price Oracles: Constant Function Market Makers. Proceedings of AFT 2020. https://arxiv.org/abs/2003.10001",
        "[3] G. Angeris, A. Agrawal, A. Evans, T. Chitra, and S. Boyd. Constant Function Market Makers: Multi-Asset Trades via Convex Optimization. 2021. https://arxiv.org/abs/2107.12484",
        "[4] NNI implementation reference. nni_server/bancor_math.mjs and nni_server/storage.mjs, commit f21375395e0204eec7f42f6c54af9a9bd5c16210, reviewed 2026-09-28.",
        "[5] NNI implementation reference. nni_server/activation_fund.mjs, one-time 100 USD qualified-participation budget policy, reviewed 2026-09-28.",
        "[6] NNI implementation reference. nni_server/activation_fund_liquidity.mjs, activation_fund_liquidity_config.mjs, and pool-price candle projections, commit f21375395e0204eec7f42f6c54af9a9bd5c16210.",
        "[7] Test-data source endpoint. https://api-1.matrixai.one/v1/nni/server/bancor/market, accessed 2026-09-28 08:30:31 CST.",
    ]
    story.extend(Paragraph(escape(ref), st["reference"]) for ref in refs)
    story += [
        Spacer(1, 2 * mm),
        Paragraph(
            "Reproducibility note: all Bancor Plus numerical results were recomputed with the current formulas. The test-data snapshot is "
            "illustrative and is not an earnings forecast, valuation opinion, or trading recommendation.",
            st["reference"],
        ),
    ]
    return story


def build_paper(language: str, output_path: Path) -> None:
    st = styles_for(language)
    title = (
        "Bancor Plus：AI 时代面向企业与团队的储备曲线算法"
        if language == "zh"
        else "Bancor Plus: A Reserve-Curve Algorithm for Enterprises and Teams in the AI Era"
    )
    doc = PaperDocTemplate(
        str(output_path),
        language,
        title,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=title,
        author="Technical Research Paper",
        subject="Bancor Plus reserve-curve market and adaptive liquidity funding",
        creator="ReportLab",
    )
    story = cover_story(language, st) + toc_story(language, st)
    story += section_zh(st) if language == "zh" else section_en(st)
    doc.multiBuild(story)


def main() -> None:
    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_paper("zh", ZH_OUTPUT)
    build_paper("en", EN_OUTPUT)
    print(ZH_OUTPUT)
    print(EN_OUTPUT)


if __name__ == "__main__":
    main()
