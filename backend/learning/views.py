from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Prefetch
from django.db.models import Avg, Count, Max
from django.contrib import messages
from .forms import CourseForm
from .models import Course, Lesson, Result, UserCourse, User, Exercise

# Пример filter(), order_by(), __ для обращения к связанной таблице
def course_list(request):
    query = request.GET.get('q', '')
    courses = (
        Course.published
        .select_related('level')
        # .filter(level__name='A1')
        .order_by('-created_at')
    )
    if query:
        courses = courses.filter(title__icontains=query) # фильтруем по названию

    return render(request, 'courses/list.html', {
        'courses': courses,
        'query': query,
        })

# # related_name и get_absolute_url.
def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects
            .select_related('level')
            .prefetch_related(
                'teachers',
                'teachers__level',
                Prefetch(
                    'lessons',
                    queryset=Lesson.objects.prefetch_related(
                        Prefetch(
                            'exercises',
                            queryset=Exercise.objects.select_related('exercise_type')
                        )
                    )
                ),
            ),
        pk=pk
    )
    lessons = course.lessons.all()
    teachers = course.teachers.all()

    return render(request, 'courses/detail.html', {
        'course': course,
        'lessons': lessons,
        'teachers': teachers,
    })

# # без selected_related
# def course_detail(request, pk):
#     course = get_object_or_404(Course, pk=pk)

#     lessons = course.lessons.all()
#     teachers = course.teachers.all()

#     return render(request, 'courses/detail.html', {
#         'course': course,
#         'lessons': lessons,
#         'teachers': teachers
#     })


def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('course').prefetch_related('exercises'),  pk=pk)
    return render(request, 'courses/lesson.html', {'lesson': lesson})

# Агрегация и аннотирование
def stats_view(request):
    # количество учеников на каждом курсе
    course_stats = Course.objects.values('title', 'level__name').annotate(
        students_count=Count('usercourse')
    )
    course_names = Course.objects.values_list('title', flat=True)

    total_courses = Course.objects.count()
    total_students = User.objects.filter(roles__name='student').count()

    has_results = Result.objects.exists()

    avg_score = Result.objects.aggregate(avg=Avg('score'))
    # максимальный балл по курсам
    best_scores = Result.objects.values('exercise__lesson__course__title') \
                                .annotate(max_score=Max('score'))
    now = timezone.now()
    active_enrollments = UserCourse.objects.filter(access_until__gt=now)

    return render(request, 'courses/stats.html', {
        'course_stats': course_stats,
        'course_names': course_names,
        'total_courses': total_courses,
        'total_students': total_students,
        'has_results': has_results,
        'avg_score': avg_score,
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
    old_level = course.level_id
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            if course.level_id != old_level:
                UserCourse.objects.filter(course=course).update(progress=0.0)
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