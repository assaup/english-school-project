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
    students_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 'lessons_count', 
                  'teachers_count', 'students_count', 'cover', 'video_url', 'created_at']


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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
    

class TeacherSerializer(serializers.ModelSerializer):
    level = LevelSerializer(read_only=True)
    courses_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'level', 'courses_count']


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'level', 'video_url', 'cover']


class LessonWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'order']

class UserCourseAdminSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField(read_only=True)
    teacher_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserCourse
        fields = ['id', 'user', 'user_display', 'teacher', 'teacher_display',
                  'progress', 'status', 'enrolled_at', 'access_until']
        read_only_fields = ['enrolled_at']

    def get_user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_teacher_display(self, obj):
        if obj.teacher:
            return obj.teacher.get_full_name() or obj.teacher.username
        return None

class UserShortSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'display', 'role']

    def get_display(self, obj):
        return obj.get_full_name() or obj.username

    def get_role(self, obj):
        role = obj.roles.filter(name__in=['teacher', 'student']).first()
        return role.name if role else None