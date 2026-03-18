import os

from django.conf import settings
from django.http import HttpResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_course_pdf(course):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="course_{course.pk}.pdf"'

    # путь к шрифту
    font_path = os.path.join(settings.BASE_DIR, "fonts", "DejaVuSans.ttf")

    pdfmetrics.registerFont(TTFont("DejaVu", font_path))

    styles = getSampleStyleSheet()

    styles["Normal"].fontName = "DejaVu"
    styles["Heading1"].fontName = "DejaVu"
    styles["Heading2"].fontName = "DejaVu"

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    elements = []

    # Заголовок курса
    elements.append(Paragraph(f"Курс: {course.title}", styles["Heading1"]))
    elements.append(Spacer(1, 20))

    # Информация о курсе
    info_data = [
        ["Уровень", str(course.level) if course.level else "—"],
        ["Дата создания", course.created_at.strftime("%d.%m.%Y")],
        ["Количество уроков", course.lessons.count()],
    ]

    table = Table(info_data, colWidths=[6 * cm, 10 * cm])

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ])
    )

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Описание курса
    elements.append(Paragraph("Описание курса", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    description = course.description or "Описание отсутствует."

    elements.append(Paragraph(description, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Список уроков
    elements.append(Paragraph("Список уроков", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    lessons = course.lessons.all().order_by("order")

    lesson_items = []

    for lesson in lessons:
        lesson_items.append(
            Paragraph(
                f"{lesson.order}. {lesson.title}",
                styles["Normal"]
            )
        )

    elements.append(
        ListFlowable(
            lesson_items,
            bulletType="bullet"
        )
    )

    # нумерация страниц
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Страница {page_num}"
        canvas.setFont("DejaVu", 9)
        canvas.drawRightString(20 * cm, 1.5 * cm, text)

    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return response