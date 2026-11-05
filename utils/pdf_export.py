from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
import re
import unicodedata

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Preformatted
)
import matplotlib

# =========================
# FONT CONFIGURATION
# =========================

def register_pdf_fonts():
    font_dir = (
        Path(matplotlib.get_data_path())
        / "fonts"
        / "ttf"
    )

    font_files = {
        "Regular": "DejaVuSans.ttf",
        "Bold": "DejaVuSans-Bold.ttf",
        "Italic": "DejaVuSans-Oblique.ttf",
        "BoldItalic": "DejaVuSans-BoldOblique.ttf"
    }

    font_names = {
        "Regular": "PDFUnicode",
        "Bold": "PDFUnicode-Bold",
        "Italic": "PDFUnicode-Italic",
        "BoldItalic": "PDFUnicode-BoldItalic"
    }

    for style, filename in font_files.items():
        font_path = font_dir / filename
        font_name = font_names[style]

        if not font_path.exists():
            raise FileNotFoundError(
                f"PDF font not found: {font_path}"
            )

        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(
                TTFont(font_name, str(font_path))
            )

    pdfmetrics.registerFontFamily(
        "PDFUnicode",
        normal="PDFUnicode",
        bold="PDFUnicode-Bold",
        italic="PDFUnicode-Italic",
        boldItalic="PDFUnicode-BoldItalic"
    )

    return font_names


# =========================
# TEXT CLEANING
# =========================

def clean_pdf_text(text):

    text = unicodedata.normalize(
        "NFKC",
        str(text)
    )

    replacements = {
        "\u00a0": " ",
        "\u200b": "",
        "\ufeff": "",
        "\ufffd": "",
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2022": "-",
        "\u2026": "...",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"'
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# =========================
# INLINE MARKDOWN
# =========================

def format_inline(text):

    pattern = (
        r'(\*\*.*?\*\*|__.*?__|'
        r'(?<!\*)\*[^*\n]+\*(?!\*)|'
        r'(?<!_)_[^_\n]+_(?!_)|'
        r'`[^`]+`|'
        r'\[.*?\]\(.*?\))'
    )

    parts = re.split(pattern, text)
    result = []

    for part in parts:

        if not part:
            continue

        # Bold
        if (
            part.startswith("**") and part.endswith("**")
        ) or (
            part.startswith("__") and part.endswith("__")
        ):

            value = escape(part[2:-2])
            result.append(f"<b>{value}</b>")

        # Italic
        elif (
            part.startswith("*") and part.endswith("*")
        ) or (
            part.startswith("_") and part.endswith("_")
        ):

            value = escape(part[1:-1])
            result.append(f"<i>{value}</i>")

        # Inline code
        elif part.startswith("`") and part.endswith("`"):

            value = escape(part[1:-1])

            result.append(
                f'<font name="PDFUnicode" size="9">'
                f'{value}</font>'
            )

        # Markdown links
        elif part.startswith("[") and "](" in part:

            match = re.match(
                r'\[(.*?)\]\((.*?)\)',
                part
            )

            if match:

                label = escape(match.group(1))
                url = escape(
                    match.group(2),
                    {'"': '&quot;'}
                )

                result.append(
                    f'<link href="{url}" color="blue">'
                    f'{label}</link>'
                )

        else:

            result.append(escape(part))

    return "".join(result)


# =========================
# MARKDOWN CONVERSION
# =========================

def convert_markdown(content, styles):

    story = []
    lines = content.splitlines()

    paragraph_lines = []
    code_lines = []
    inside_code = False

    def add_paragraph():

        if paragraph_lines:

            text = " ".join(paragraph_lines)

            story.append(
                Paragraph(
                    format_inline(text),
                    styles["Normal"]
                )
            )

            story.append(Spacer(1, 6))
            paragraph_lines.clear()

    for line in lines:

        stripped = line.strip()

        # Code block
        if stripped.startswith("```"):

            add_paragraph()

            if inside_code:

                code = "\n".join(code_lines)

                story.append(
                    Preformatted(
                        escape(code),
                        styles["CodeBlock"]
                    )
                )

                story.append(Spacer(1, 8))

                code_lines.clear()
                inside_code = False

            else:

                inside_code = True

            continue

        if inside_code:

            code_lines.append(line)
            continue

        # Empty line
        if not stripped:

            add_paragraph()
            continue

        # Horizontal separator
        if re.fullmatch(r'([-*_]\s*){3,}', stripped):

            add_paragraph()

            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.7,
                    color=colors.lightgrey
                )
            )

            story.append(Spacer(1, 8))
            continue

        # Headings
        heading = re.match(
            r'^(#{1,6})\s+(.+)$',
            stripped
        )

        if heading:

            add_paragraph()

            level = len(heading.group(1))
            style_name = f"PDFHeading{min(level, 3)}"

            story.append(
                Paragraph(
                    format_inline(heading.group(2)),
                    styles[style_name]
                )
            )

            story.append(Spacer(1, 5))
            continue

        # Bullet lists
        bullet = re.match(
            r'^[-*+]\s+(.+)$',
            stripped
        )

        if bullet:

            add_paragraph()

            story.append(
                Paragraph(
                    format_inline(bullet.group(1)),
                    styles["Normal"],
                    bulletText="-"
                )
            )

            story.append(Spacer(1, 3))
            continue

        # Numbered lists
        numbered = re.match(
            r'^(\d+)[.)]\s+(.+)$',
            stripped
        )

        if numbered:

            add_paragraph()

            story.append(
                Paragraph(
                    format_inline(numbered.group(2)),
                    styles["Normal"],
                    bulletText=numbered.group(1) + "."
                )
            )

            story.append(Spacer(1, 3))
            continue

        paragraph_lines.append(stripped)

    add_paragraph()

    # Handle unfinished code block
    if inside_code and code_lines:

        story.append(
            Preformatted(
                escape("\n".join(code_lines)),
                styles["CodeBlock"]
            )
        )

    return story


# =========================
# PDF GENERATION
# =========================

def generate_chat_pdf(pdf_name, messages):

    fonts = register_pdf_fonts()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch
    )

    styles = getSampleStyleSheet()

    # Normal text
    styles["Normal"].fontName = fonts["Regular"]
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 15

    # Main title
    styles.add(
        ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontName=fonts["Bold"],
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontSize=20,
            spaceAfter=15
        )
    )

    # Message heading
    styles.add(
        ParagraphStyle(
            "MessageHeading",
            parent=styles["Normal"],
            fontName=fonts["Bold"],
            fontSize=11,
            leading=15,
            spaceAfter=5
        )
    )

    # Custom heading styles
    for level, size in [(1, 16), (2, 14), (3, 12)]:

        styles.add(
            ParagraphStyle(
                f"PDFHeading{level}",
                parent=styles[f"Heading{level}"],
                fontName=fonts["Bold"],
                fontSize=size,
                leading=size + 4,
                spaceBefore=8,
                spaceAfter=6
            )
        )

    # Code block
    styles.add(
        ParagraphStyle(
            "CodeBlock",
            fontName=fonts["Regular"],
            fontSize=8,
            leading=11,
            backColor=colors.whitesmoke,
            borderPadding=7,
            spaceBefore=5,
            spaceAfter=8
        )
    )

    story = []

    # Document title
    story.append(
        Paragraph(
            "PDF Chat Conversation",
            styles["CustomTitle"]
        )
    )

    # Original PDF name
    story.append(
        Paragraph(
            f"<b>Document:</b> "
            f"{escape(clean_pdf_text(pdf_name))}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    # Conversation messages
    for msg in messages:

        role = msg["role"]
        content = clean_pdf_text(msg["content"])

        if role == "user":

            heading = "You"
            heading_color = colors.darkblue

        elif role == "assistant":

            heading = "Assistant"
            heading_color = colors.darkgreen

        else:

            continue

        story.append(
            Paragraph(
                f'<font name="{fonts["Bold"]}" '
                f'color="{heading_color.hexval()}">'
                f'{heading}:</font>',
                styles["MessageHeading"]
            )
        )

        story.extend(
            convert_markdown(
                content,
                styles
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.lightgrey
            )
        )

        story.append(Spacer(1, 10))

    # Build PDF
    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()