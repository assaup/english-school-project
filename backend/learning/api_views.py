from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Max
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Course, Lesson, Result, UserCourse, Level, Role, User, TeacherCourse, UserRole
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseWriteSerializer,
    LessonWriteSerializer, UserCourseAdminSerializer,
    UserShortSerializer,
    UserSerializer, UserCourseSerializer,
    RegisterSerializer, TeacherSerializer,
    LevelSerializer
)


class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'level__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Course.published
            .select_related('level')
            .prefetch_related('teachers')
            .annotate(students_count=Count('usercourse', distinct=True))  # ← добавь
        )
    

class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        return Course.objects.select_related('level').prefetch_related('teachers', 'lessons__exercises')
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses_view(request):
    enrollments = UserCourse.objects.filter(user=request.user).select_related('course__level')
    serializer = UserCourseSerializer(enrollments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def stats_view(request):
    total_courses = Course.objects.count()
    total_students = Course.objects.aggregate(total=Count('students'))['total']
    avg_score = Result.objects.aggregate(avg=Avg('score'))['avg']
    course_stats = list(
        Course.objects.values('title', 'level__name').annotate(
            students_count=Count('usercourse'),
            avg_score=Avg('usercourse__user__result__score')
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
    # Секция 1 Поиск
    query = request.GET.get('q', '').strip()

    courses = (
        Course.published
        .select_related('level')
        .prefetch_related('teachers')
        .annotate(
            lessons_count=Count('lessons', distinct=True),
            students_count=Count('usercourse', distinct=True)
        )
        .order_by('-created_at')
    )
    if query:
        courses = courses.filter(title__icontains=query)

    # Секция 2 Преподаватели
    teacher_role = Role.objects.filter(name='Преподаватель').first()

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

    # Секция 3 Статистика
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
    top_level_name = top_level_data['level__name'] if top_level_data else None
    
    return Response({
        'courses': CourseListSerializer(courses, many=True, context={'request': request}).data,
        'query': query,
        'teachers': TeacherSerializer(teachers, many=True).data,
        'stats': {
            'total_courses': total_courses,
            'total_lessons': total_lessons,
            'total_students': total_students,
            'avg_score': round(avg_score, 1) if avg_score else None,
            'top_level': top_level_name,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def course_create_view(request):
    serializer = CourseWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    course = serializer.save()
    return Response(CourseDetailSerializer(course).data, status=201)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def course_update_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    serializer = CourseWriteSerializer(course, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    course = serializer.save()
    return Response(CourseDetailSerializer(course).data)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def course_delete_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([AllowAny])
def levels_view(request):
    levels = Level.objects.all()
    return Response(LevelSerializer(levels, many=True).data)


# --- Уроки ---
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_lessons_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'GET':
        lessons = Lesson.objects.filter(course=course).order_by('order')
        return Response(LessonWriteSerializer(lessons, many=True).data)

    serializer = LessonWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(course=course)
    return Response(serializer.data, status=201)


@api_view(['PATCH', 'DELETE'])
@permission_classes([AllowAny])
def lesson_detail_view(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)

    if request.method == 'PATCH':
        serializer = LessonWriteSerializer(lesson, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    lesson.delete()
    return Response(status=204)


# Преподаватели курса
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_teachers_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'GET':
        teachers = course.teachers.all()
        return Response(UserShortSerializer(teachers, many=True).data)

    user_id = request.data.get('user_id')
    user = get_object_or_404(User, pk=user_id)
    TeacherCourse.objects.get_or_create(course=course, teacher=user)
    teachers = course.teachers.all()
    return Response(UserShortSerializer(teachers, many=True).data, status=201)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def course_teacher_remove_view(request, pk, user_id):
    course = get_object_or_404(Course, pk=pk)
    TeacherCourse.objects.filter(course=course, teacher_id=user_id).delete()
    return Response(status=204)


# Записи на курс 
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_enrollments_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'GET':
        enrollments = UserCourse.objects.filter(course=course).select_related('user', 'teacher')
        return Response(UserCourseAdminSerializer(enrollments, many=True).data)

    serializer = UserCourseAdminSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(course=course)
    return Response(serializer.data, status=201)


@api_view(['PATCH', 'DELETE'])
@permission_classes([AllowAny])
def enrollment_detail_view(request, pk):
    enrollment = get_object_or_404(UserCourse, pk=pk)

    if request.method == 'PATCH':
        serializer = UserCourseAdminSerializer(enrollment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    enrollment.delete()
    return Response(status=204)


# Все пользователи
@api_view(['GET'])
@permission_classes([AllowAny])
def users_view(request):
    role = request.GET.get('role')
    users = User.objects.all()
    if role:
        users = users.filter(roles__name=role)
    return Response(UserShortSerializer(users, many=True).data)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_set_role_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    role_name = request.data.get('role')  # 'teacher' или 'student'

    if role_name not in ('teacher', 'student'):
        return Response({'error': 'Допустимые роли: teacher, student'}, status=400)

    # убираем обе роли, назначаем одну
    Role.objects.filter(name__in=['teacher', 'student']).exclude(name=role_name).values_list('id', flat=True)
    UserRole.objects.filter(user=user, role__name__in=['teacher', 'student']).delete()
    role = Role.objects.get(name=role_name)
    UserRole.objects.get_or_create(user=user, role=role)

    return Response({'status': 'ok', 'role': role_name})