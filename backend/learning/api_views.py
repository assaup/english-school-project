from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Prefetch
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import Course, Lesson, Result, UserCourse, Level, Role, User, TeacherCourse, UserRole
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseWriteSerializer,
    LessonWriteSerializer, UserCourseAdminSerializer, EnrollmentSerializer,
    UserShortSerializer, UserSerializer, UserCourseSerializer,
    RegisterSerializer, TeacherSerializer, LevelSerializer,
    ResultSerializer, ResultCreateSerializer,
)
from .permissions import IsAdminRole, IsAdminOrTeacher
from .filters import CourseFilter


def _annotate_courses(qs):
    """Добавляет к queryset курсов аннотации счётчиков и среднего балла."""
    return qs.annotate(
        students_count=Count('usercourse', distinct=True),
        lessons_count=Count('lessons', distinct=True),
        teachers_count=Count('teachercourse', distinct=True),
        avg_score=Avg('lessons__exercises__result__score'),
    )


class CourseListView(generics.ListAPIView):
    """Публичный список опубликованных курсов с поиском, сортировкой и фильтрацией."""

    serializer_class = CourseListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description', 'level__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return _annotate_courses(
            Course.published
            .select_related('level')
            .prefetch_related('teachers')
        ).distinct()


class CourseDetailView(generics.RetrieveAPIView):
    """Детальная страница курса."""

    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        return Course.objects.select_related('level').prefetch_related('teachers', 'lessons__exercises')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Возвращает профиль текущего пользователя."""
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses_view(request):
    """Возвращает курсы, на которые записан текущий пользователь (с аннотациями)."""
    annotated_courses = _annotate_courses(
        Course.objects.select_related('level').prefetch_related('teachers')
    )
    enrollments = (
        UserCourse.objects
        .filter(user=request.user)
        .select_related('teacher')
        .prefetch_related(Prefetch('course', queryset=annotated_courses))
    )
    return Response(UserCourseSerializer(enrollments, many=True, context={'request': request}).data)


@api_view(['GET'])
def stats_view(request):
    """Общая статистика платформы."""
    total_courses = Course.objects.count()
    total_students = Course.objects.aggregate(total=Count('students'))['total']
    avg_score = Result.objects.aggregate(avg=Avg('score'))['avg']
    course_stats = list(
        Course.objects.values('title', 'level__name').annotate(
            students_count=Count('usercourse'),
            avg_score=Avg('usercourse__user__result__score'),
        )
    )
    return Response({
        'total_courses': total_courses,
        'total_students': total_students,
        'avg_score': round(avg_score, 1) if avg_score else None,
        'course_stats': course_stats,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Регистрация нового пользователя. Возвращает JWT-токены."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }, status=201)


@api_view(['GET'])
@permission_classes([AllowAny])
def home_view(request):
    """Главная страница: курсы, преподаватели, статистика."""
    query = request.GET.get('q', '').strip()

    courses = _annotate_courses(
        Course.published
        .select_related('level')
        .prefetch_related('teachers')
    ).order_by('-created_at').distinct()

    if query:
        courses = courses.filter(title__icontains=query)

    teacher_role = Role.objects.filter(name='teacher').first()
    if teacher_role:
        teachers = (
            User.objects
            .filter(roles=teacher_role)
            .select_related('level')
            .annotate(courses_count=Count('teacher_courses', distinct=True))
            .order_by('-courses_count')
        )
    else:
        teachers = (
            User.objects
            .exclude(teacher_courses=None)
            .select_related('level')
            .annotate(courses_count=Count('teacher_courses', distinct=True))
            .order_by('-courses_count')
        )

    total_courses = Course.objects.count()
    total_lessons = Lesson.objects.count()
    total_students = User.objects.filter(roles__name='student').count()
    avg_score = Result.objects.aggregate(avg=Avg('score'))['avg']

    top_level_data = (
        Course.objects
        .exclude(level=None)
        .values('level__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    return Response({
        'courses': CourseListSerializer(courses, many=True, context={'request': request}).data,
        'query': query,
        'teachers': TeacherSerializer(teachers, many=True).data,
        'stats': {
            'total_courses': total_courses,
            'total_lessons': total_lessons,
            'total_students': total_students,
            'avg_score': round(avg_score, 1) if avg_score else None,
            'top_level': top_level_data['level__name'] if top_level_data else None,
        },
    })


@api_view(['POST'])
@permission_classes([IsAdminOrTeacher])
def course_create_view(request):
    """Создание курса. Доступно только admin и teacher."""
    serializer = CourseWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    course = serializer.save()
    return Response(CourseDetailSerializer(course, context={'request': request}).data, status=201)


@api_view(['PATCH'])
@permission_classes([IsAdminOrTeacher])
def course_update_view(request, pk):
    """Редактирование курса. Доступно только admin и teacher."""
    course = get_object_or_404(Course, pk=pk)
    serializer = CourseWriteSerializer(course, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    course = serializer.save()
    return Response(CourseDetailSerializer(course, context={'request': request}).data)


@api_view(['DELETE'])
@permission_classes([IsAdminRole])
def course_delete_view(request, pk):
    """Удаление курса. Доступно только admin."""
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([AllowAny])
def levels_view(request):
    """Список всех уровней языка."""
    return Response(LevelSerializer(Level.objects.all(), many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_lessons_view(request, pk):
    """Список уроков курса (GET — публично, POST — только admin/teacher)."""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'GET':
        lessons = Lesson.objects.filter(course=course).order_by('order')
        return Response(LessonWriteSerializer(lessons, many=True).data)

    if not (request.user.is_authenticated and
            request.user.roles.filter(name__in=['admin', 'teacher']).exists()):
        return Response({'detail': 'Доступ запрещён.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = LessonWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(course=course)
    return Response(serializer.data, status=201)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminOrTeacher])
def lesson_detail_view(request, pk):
    """Редактирование / удаление урока. Доступно только admin и teacher."""
    lesson = get_object_or_404(Lesson, pk=pk)

    if request.method == 'PATCH':
        serializer = LessonWriteSerializer(lesson, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    lesson.delete()
    return Response(status=204)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_teachers_view(request, pk):
    """Преподаватели курса (GET — публично, POST — только admin)."""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'GET':
        return Response(UserShortSerializer(course.teachers.all(), many=True).data)

    if not (request.user.is_authenticated and
            request.user.roles.filter(name='admin').exists()):
        return Response({'detail': 'Доступ запрещён.'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    user = get_object_or_404(User, pk=user_id)
    TeacherCourse.objects.get_or_create(course=course, teacher=user)
    return Response(UserShortSerializer(course.teachers.all(), many=True).data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAdminRole])
def course_teacher_remove_view(request, pk, user_id):
    """Удаление преподавателя с курса. Доступно только admin."""
    course = get_object_or_404(Course, pk=pk)
    TeacherCourse.objects.filter(course=course, teacher_id=user_id).delete()
    return Response(status=204)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrTeacher])
def course_enrollments_view(request, pk):
    """Управление записями студентов на курс. Доступно только admin и teacher."""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'GET':
        enrollments = UserCourse.objects.filter(course=course).select_related('user', 'teacher')
        return Response(UserCourseAdminSerializer(enrollments, many=True).data)

    serializer = EnrollmentSerializer(
        data=request.data,
        context={'request': request, 'course': course},
    )
    serializer.is_valid(raise_exception=True)
    enrollment = serializer.save(course=course)
    return Response(UserCourseAdminSerializer(enrollment).data, status=201)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminOrTeacher])
def enrollment_detail_view(request, pk):
    """Редактирование / удаление записи студента. Доступно только admin и teacher."""
    enrollment = get_object_or_404(UserCourse, pk=pk)

    if request.method == 'PATCH':
        serializer = UserCourseAdminSerializer(enrollment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    enrollment.delete()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAdminRole])
def users_view(request):
    """Список всех пользователей. Доступно только admin."""
    role = request.GET.get('role')
    users = User.objects.all()
    if role:
        users = users.filter(roles__name=role)
    return Response(UserShortSerializer(users, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminRole])
def user_set_role_view(request, pk):
    """Назначение роли пользователю. Доступно только admin."""
    user = get_object_or_404(User, pk=pk)
    role_name = request.data.get('role')

    if role_name not in ('teacher', 'student'):
        return Response({'error': 'Допустимые роли: teacher, student'}, status=400)

    UserRole.objects.filter(user=user, role__name__in=['teacher', 'student']).delete()
    role = Role.objects.get(name=role_name)
    UserRole.objects.get_or_create(user=user, role=role)
    return Response({'status': 'ok', 'role': role_name})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def results_view(request):
    """
    GET  — список результатов (admin/teacher видят все, student — только свои).
    POST — отправить результат выполнения задания.
    """
    if request.method == 'GET':
        if request.user.roles.filter(name__in=['admin', 'teacher']).exists():
            results = Result.objects.select_related('exercise', 'user').all()
        else:
            results = Result.objects.filter(user=request.user).select_related('exercise')
        return Response(ResultSerializer(results, many=True).data)

    serializer = ResultCreateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    result = serializer.save(user=request.user)
    return Response(ResultSerializer(result).data, status=201)
