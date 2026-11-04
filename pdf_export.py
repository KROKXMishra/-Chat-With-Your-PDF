
import os
import reportlab

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable
)


# -------------------- FONT REGISTRATION --------------------

font_dir = os.path.join(
    os.path.dirname(reportlab.__file__),
    "fonts"
)

regular_font = os.path.join(font_dir, "Vera.ttf")
bold_font = os.path.join(font_dir, "VeraBd.ttf")

pdfmetrics.registerFont(
    TTFont("Vera", regular_font)
)

pdfmetrics.registerFont(
    TTFont("Vera-Bold", bold_font)
)

pdfmetrics.registerFontFamily(
    "Vera",
    normal="Vera",
    bold="Vera-Bold",
    italic="Vera",
    boldItalic="Vera-Bold"
)


# -------------------- PDF GENERATION --------------------

def generate_chat_pdf(pdf_name, messages, chat_date):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch
    )

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "Vera"

    title_style = ParagraphStyle(
        "ChatTitle",
        parent=styles["Title"],
        fontName="Vera-Bold",
        fontSize=18,
        leading=24,
        textColor=colors.HexColor("#1F4E79"),
        alignment=TA_CENTER,
        spaceAfter=12
    )

    info_style = ParagraphStyle(
        "Info",
        parent=styles["Normal"],
        fontName="Vera",
        fontSize=9,
        leading=13,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=15
    )

    question_style = ParagraphStyle(
        "Question",
        parent=styles["Normal"],
        fontName="Vera",
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#1F4E79"),
        spaceAfter=8,
        wordWrap="CJK"
    )

    answer_style = ParagraphStyle(
        "Answer",
        parent=styles["Normal"],
        fontName="Vera",
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#222222"),
        spaceAfter=12,
        wordWrap="CJK"
    )

    timestamp_style = ParagraphStyle(
        "Timestamp",
        parent=styles["Normal"],
        fontName="Vera",
        fontSize=8,
        leading=11,
        textColor=colors.grey,
        spaceAfter=8
    )

    story = []

    # Document heading
    story.append(
        Paragraph(
            "PDF Chatbot - Conversation History",
            title_style
        )
    )

    # PDF information
    story.append(
        Paragraph(
            f"PDF: {escape(str(pdf_name))} | "
            f"Date: {escape(str(chat_date))}",
            info_style
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.lightgrey
        )
    )

    story.append(Spacer(1, 18))

    # Add every question and answer
    for role, content, timestamp in messages:

        safe_content = escape(str(content))
        safe_content = safe_content.replace("\n", "<br/>")

        if role == "user":

            story.append(
                Paragraph(
                    f"<b>Question:</b><br/>{safe_content}",
                    question_style
                )
            )

        else:

            story.append(
                Paragraph(
                    f"<b>AI Assistant:</b><br/>{safe_content}",
                    answer_style
                )
            )

        story.append(
            Paragraph(
                escape(str(timestamp)),
                timestamp_style
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.lightgrey
            )
        )

        story.append(Spacer(1, 12))

    # Generate PDF
    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()
