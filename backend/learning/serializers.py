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
        fields = ['id', 'name']


class ExerciseSerializer(serializers.ModelSerializer):
    exercise_type = ExerciseTypeSerializer(read_only=True)

    class Meta:
        model = Exercise
        fields = ['id', 'question', 'correct_answer', 'exercise_type', 'order']


class LessonSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'order', 'exercises']


class CourseListSerializer(serializers.ModelSerializer):
    """Список курсов с аннотированными счётчиками и флагом записи текущего пользователя."""

    level = LevelSerializer(read_only=True)
    # Поля заполняются через аннотации queryset (.annotate(...))
    lessons_count = serializers.IntegerField(read_only=True)
    teachers_count = serializers.IntegerField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    avg_score = serializers.FloatField(read_only=True, allow_null=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'level',
            'lessons_count', 'teachers_count', 'students_count',
            'avg_score', 'is_enrolled',
            'cover', 'video_url', 'created_at',
        ]

    def get_is_enrolled(self, obj) -> bool:
        """Возвращает True, если текущий пользователь записан на курс."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserCourse.objects.filter(user=request.user, course=obj).exists()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Детальная страница курса с уроками, преподавателями и флагом записи."""

    level = LevelSerializer(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    teachers = UserSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'level',
            'lessons', 'teachers', 'is_enrolled',
            'cover', 'video_url', 'created_at',
        ]

    def get_is_enrolled(self, obj) -> bool:
        """Возвращает True, если текущий пользователь записан на курс."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserCourse.objects.filter(user=request.user, course=obj).exists()


class ResultSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = Result
        fields = ['id', 'exercise', 'user_answer', 'score', 'completed_at']


class ResultCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для отправки результата выполнения задания."""

    class Meta:
        model = Result
        fields = ['id', 'exercise', 'user_answer', 'score', 'completed_at']
        read_only_fields = ['completed_at']

    def validate_score(self, value: int) -> int:
        """Балл должен быть в диапазоне 0–100."""
        if not 0 <= value <= 100:
            raise serializers.ValidationError('Балл должен быть от 0 до 100.')
        return value

    def validate(self, attrs: dict) -> dict:
        """Студент может выполнять задания только курсов, на которые он записан."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            if not user.roles.filter(name__in=['admin', 'teacher']).exists():
                exercise = attrs.get('exercise')
                course = exercise.lesson.course
                if not UserCourse.objects.filter(user=user, course=course).exists():
                    raise serializers.ValidationError(
                        {'exercise': 'Вы не записаны на курс этого задания.'}
                    )
        return attrs


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

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return attrs

    def create(self, validated_data: dict) -> User:
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


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


class EnrollmentSerializer(serializers.ModelSerializer):
    """Сериализатор для записи студента на курс (с валидацией дубликатов и прогресса)."""

    class Meta:
        model = UserCourse
        fields = ['id', 'user', 'teacher', 'progress', 'status', 'access_until', 'enrolled_at']
        read_only_fields = ['enrolled_at']

    def validate_progress(self, value: float) -> float:
        """Прогресс должен быть в диапазоне 0–100."""
        if not 0 <= value <= 100:
            raise serializers.ValidationError('Прогресс должен быть от 0 до 100.')
        return value

    def validate(self, attrs: dict) -> dict:
        """Студент не может быть записан на один курс дважды."""
        user = attrs.get('user')
        course = self.context.get('course')
        if user and course:
            existing = UserCourse.objects.filter(user=user, course=course)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError(
                    {'user': 'Этот студент уже записан на данный курс.'}
                )
        return attrs


class UserCourseAdminSerializer(serializers.ModelSerializer):
    """Сериализатор управления записями студентов (для администратора/преподавателя)."""

    user_display = serializers.SerializerMethodField(read_only=True)
    teacher_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserCourse
        fields = [
            'id', 'user', 'user_display', 'teacher', 'teacher_display',
            'progress', 'status', 'enrolled_at', 'access_until',
        ]
        read_only_fields = ['enrolled_at']

    def get_user_display(self, obj) -> str:
        return obj.user.get_full_name() or obj.user.username

    def get_teacher_display(self, obj) -> str | None:
        if obj.teacher:
            return obj.teacher.get_full_name() or obj.teacher.username
        return None

    def validate_progress(self, value: float) -> float:
        """Прогресс должен быть в диапазоне 0–100."""
        if not 0 <= value <= 100:
            raise serializers.ValidationError('Прогресс должен быть от 0 до 100.')
        return value


class UserShortSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'display', 'role']

    def get_display(self, obj) -> str:
        return obj.get_full_name() or obj.username

    def get_role(self, obj) -> str | None:
        role = obj.roles.filter(name__in=['teacher', 'student']).first()
        return role.name if role else None
