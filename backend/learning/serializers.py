from rest_framework import serializers
from .models import Course, Lesson, Exercise, ExerciseType, Level, User, Result, UserCourse


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name', 'description']


class UserSerializer(serializers.ModelSerializer):
    level = LevelSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'level']


class ExerciseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseType
        fields=['id', 'name']


class ExerciseSerializer(serializers.ModelSerializer):
    exercise_type = ExerciseTypeSerializer(read_only=True)
    class Meta:
        model = Exercise
        fields=['id', 'question', 'correct_answer', 'exercise_type', 'order']


class LessonSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)
    class Meta:
        model = Lesson
        fields=['id', 'title', 'description', 'order', 'exercises']


class CourseListSerializer(serializers.ModelSerializer):
    level = LevelSerializer(read_only=True)
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)
    teachers_count = serializers.IntegerField(source='teachers.count', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 'lessons_count', 'teachers_count', 'cover', 'video_url', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    level = LevelSerializer(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    teachers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 'lessons', 'teachers', 'cover', 'video_url', 'created_at']


class ResultSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = Result
        fields = ['id', 'exercise', 'user_answer', 'score', 'completed_at']


class UserCourseSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = UserCourse
        fields = ['id', 'course', 'progress', 'status', 'enrolled_at', 'access_until']
