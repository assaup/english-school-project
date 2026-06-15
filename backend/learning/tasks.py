from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def send_enrollment_email(user_email: str, user_name: str, course_title: str) -> str:
    """Отправляет письмо студенту при записи на курс (перехватывается Mailhog)."""
    subject = f'Вы записаны на курс: {course_title}'
    message = (
        f'Привет, {user_name}!\n\n'
        f'Вы успешно записаны на курс «{course_title}».\n'
        f'Желаем успехов в обучении!\n\n'
        f'— Команда ENGLOBE'
    )
    send_mail(
        subject=subject,
        message=message,
        from_email='noreply@englobe.com',
        recipient_list=[user_email],
        fail_silently=False,
    )
    return f'Email отправлен на {user_email}'


@shared_task
def mark_expired_enrollments() -> str:
    """
    Переводит активные записи с истёкшим access_until в статус 'finished'.
    Запускается периодически через Celery Beat.
    """
    from .models import UserCourse
    now = timezone.now()
    updated = UserCourse.objects.filter(
        access_until__lt=now,
        status=UserCourse.Status.ACTIVE,
    ).update(status=UserCourse.Status.FINISHED)
    return f'Обновлено записей: {updated}'
