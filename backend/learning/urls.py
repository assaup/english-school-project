from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import api_views

urlpatterns = [
    # REST API
    path('api/courses/', api_views.CourseListView.as_view(), name='api_course_list'),
    path('api/courses/<int:pk>/', api_views.CourseDetailView.as_view(), name='api_course_detail'),
    path('api/me/', api_views.me_view, name='api_me'),
    path('api/my-courses/', api_views.my_courses_view, name='api_my_courses'),
    path('api/stats/', api_views.stats_view, name='api_stats'),
    path('api/auth/register/', api_views.register_view, name='api_register'),
    path('api/home/', api_views.home_view, name='api_home'),
    path('api/courses/create/', api_views.course_create_view, name='api_course_create'),
    path('api/courses/<int:pk>/update/', api_views.course_update_view, name='api_course_update'),
    path('api/courses/<int:pk>/delete/', api_views.course_delete_view, name='api_course_delete'),
    path('api/levels/', api_views.levels_view, name='api_levels'),
    # Уроки
    path('api/courses/<int:pk>/lessons/', api_views.course_lessons_view, name='api_course_lessons'),
    path('api/lessons/<int:pk>/', api_views.lesson_detail_view, name='api_lesson_detail'),

    # Преподаватели курса
    path('api/courses/<int:pk>/teachers/', api_views.course_teachers_view, name='api_course_teachers'),
    path('api/courses/<int:pk>/teachers/<int:user_id>/', api_views.course_teacher_remove_view, name='api_course_teacher_remove'),

    # Записи
    path('api/courses/<int:pk>/enrollments/', api_views.course_enrollments_view, name='api_course_enrollments'),
    path('api/enrollments/<int:pk>/', api_views.enrollment_detail_view, name='api_enrollment_detail'),

    # Пользователи
    path('api/users/', api_views.users_view, name='api_users'),
    path('api/users/<int:pk>/role/', api_views.user_set_role_view, name='api_user_set_role'),

    # JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]