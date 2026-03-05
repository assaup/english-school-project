from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse


def generate_course_pdf(course):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="course_{course.pk}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Course: {course.title}")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Level: {course.level}")
    p.drawString(50, height - 100, f"Description: {course.description[:100]}")

    y = height - 140
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Lessons:")
    y -= 20

    p.setFont("Helvetica", 12)
    for lesson in course.lessons.all():
        p.drawString(70, y, f"{lesson.order}. {lesson.title}")
        y -= 20
        if y < 50:  # новая страница если место кончилось
            p.showPage()
            y = height - 50

    p.save()
    return response