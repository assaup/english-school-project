from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count, Max
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Course, Lesson, Result, UserCourse
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    LessonSerializer, ResultSerializer,
    UserSerializer, UserCourseSerializer,
    RegisterSerializer
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
