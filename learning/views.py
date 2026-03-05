from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Avg, Count, Max
from django.contrib import messages
from .forms import CourseForm
from .models import Course, Lesson, Result, UserCourse

# Пример filter(), order_by(), __ для обращения к связанной таблице
def course_list(request):
    courses = (
        Course.objects
        .select_related('level')
        # .filter(level__name='A1')
        .exclude(lessons__isnull=True)
        .distinct()
        .order_by('-created_at')
    )

    return render(request, 'courses/list.html', {'courses': courses})

# related_name и get_absolute_url.
def course_detail(request, pk):
    course = get_object_or_404(Course.objects.select_related('level').prefetch_related('lessons', 'teachers'), pk=pk)
    lessons = course.lessons.all() #уже в кэше
    teachers = course.teachers.all()
    return render(request, 'courses/detail.html', {'course': course, 'lessons': lessons, 'teachers': teachers})

def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('course').prefetch_related('exercises'),  pk=pk)
    return render(request, 'courses/lesson.html', {'lesson': lesson})

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

def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Курс "{course.title}" создан!')
            return redirect(course.get_absolute_url())
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Создать курс'})

def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Курс "{course.title}" обновлён!')
            return redirect(course.get_absolute_url())
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Редактировать курс'})


def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f'Курс "{title}" удалён!')
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})