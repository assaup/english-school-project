from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import api_views

urlpatterns = [
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('stats/', views.stats_view, name='stats'),

    # REST API
    path('api/courses/', api_views.CourseListView.as_view(), name='api_course_list'),
    path('api/courses/<int:pk>/', api_views.CourseDetailView.as_view(), name='api_course_detail'),
    path('api/me/', api_views.me_view, name='api_me'),
    path('api/my-courses/', api_views.my_courses_view, name='api_my_courses'),
    path('api/stats/', api_views.stats_view, name='api_stats'),
    path('api/auth/register/', api_views.register_view, name='api_register'),
    path('api/home/', api_views.home_view, name='api_home'),

    # JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]