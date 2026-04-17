from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count, Max
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Course, Lesson, Result, UserCourse, Level, Role, User
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    LessonSerializer, ResultSerializer,
    UserSerializer, UserCourseSerializer,
    RegisterSerializer, TeacherSerializer
)


class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'level__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Course.published.select_related('level').prefetch_related('teachers')
    

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
        .values('level__id', 'level__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    if top_level_data:
        try: 
            top_level = Level.objects.get(pk=top_level_data['level__id'])
            top_level_name = top_level.name
        except Level.DoesNotExist:
            top_level_name = None
    else: 
        top_level_name = None
    
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
 