from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Count, Max
from .models import Course, Lesson, Result, UserCourse

# Пример filter(), order_by(), __ для обращения к связанной таблице
def course_list(request):
    courses = Course.objects.filter(level__name='A1') 

    courses = courses.exclude(lessons__isnull=True).distinct()

    courses = courses.order_by('-created_at')

    return render(request, 'courses/list.html', {'courses': courses})

# related_name и get_absolute_url.
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lessons.all()
    return render(request, 'courses/detail.html', {'course': course, 'lessons': lessons})

# Агрегация и аннотирование
def stats_view(request):
    from django.db.models import Avg, Count, Max

    # Средний балл по всем результатам
    avg_score = Result.objects.aggregate(avg=Avg('score'))

    # Количество учеников на каждом курсе
    courses = Course.objects.annotate(students_count=Count('usercourse'))

    # Максимальный балл по каждому заданию
    best_scores = Result.objects.values('exercise__lesson__course__title') \
                                .annotate(max_score=Max('score'))

    # активные записи на курс
    now = timezone.now()
    active_enrollments = UserCourse.objects.filter(
        access_until__gt=now  #__gt = greater than (больше чем)
    )

    return render(request, 'courses/stats.html', {
        'avg_score': avg_score,
        'courses': courses,
        'best_scores': best_scores,
        'active_enrollments': active_enrollments,
    })