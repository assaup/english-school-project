from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Название роли"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Роль")
        verbose_name_plural = _("Роли")


class Level(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Уровень"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Уровень")
        verbose_name_plural = _("Уровни")


class User(AbstractUser):
    # username, email, password, first_name, last_name — уже есть в AbstractUser
    level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Уровень языка")
    )
    roles = models.ManyToManyField(
        Role,
        through='UserRole',
        related_name='users',
        verbose_name=_("Роли")
    )
    def __str__(self):
        return self.get_full_name() or self.username
    
    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_("Роль"))
    
    class Meta:
        unique_together = ('user', 'role')
        verbose_name = _("Связь пользователь-роль")
        verbose_name_plural = _("Связи пользователь-роль")

    def __str__(self):
        return f"{self.user} — {self.role}"
    

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Название курса"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Уровень")
    )
    teachers = models.ManyToManyField(
        User,
        through='TeacherCourse',
        related_name='teaching_courses',
        verbose_name=_("Преподаватели")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Курс")
        verbose_name_plural = _("Курсы")


class TeacherCourse(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_courses',
        verbose_name=_("Преподаватель")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,

        verbose_name=_("Курс")
    )

    class Meta:
        unique_together = ('teacher', 'course'),
        verbose_name = _("Назначение преподавателей")
        verbose_name_plural = _("Назначения преподавателей")

    def __str__(self):
        return f"{self.teacher} — {self.course}"
    

class UserCourse(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrolled_courses',
        verbose_name=_("Ученик")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_("Курс")
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_courses',
        verbose_name=_("Выбранный преподаватель")
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата записи"))
    progress = models.FloatField(default=0.0, verbose_name=_("Прогресс (%)"))

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = _("Запись на курс")
        verbose_name_plural = _("Записи на курсы")

    def __str__(self):
        return f"{self.user} → {self.course} ({self.progress:.0f}%)"


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Название урока"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    order = models.PositiveBigIntegerField(default=0, verbose_name=_("Порядок"))
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_("Курс")
    )

    class Meta:
        ordering = ['order']
        verbose_name = _("Урок")
        verbose_name_plural = _("Уроки")

    def __str__(self):
        return f"{self.order}. {self.title} ({self.course})"


class ExerciseType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Тип задания"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тип задания")
        verbose_name_plural = _("Типы заданий")


class Exercise(models.Model):
    question = models.TextField(verbose_name=_("Вопрос / Задание"))
    correct_answer = models.TextField(blank=True, verbose_name=_("Правильный ответ"))
    exercise_type = models.ForeignKey(
        ExerciseType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Тип")
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='exercises',
        verbose_name=_("Урок")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))

    class Meta:
        ordering = ['order']
        verbose_name = _("Задание")
        verbose_name_plural = _("Задания")

    def __str__(self):
        short = self.question[:50]
        suffix = "..." if len(self.question) > 50 else ""
        return f"{self.order}. {short}{suffix}"


class Result(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Ученик")
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        verbose_name=_("Задание")
    )
    user_answer = models.TextField(blank=True, verbose_name=_("Ответ ученика"))
    score = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=("Балл (%)")
    )
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата выполнения"))

    class Meta:
        unique_together = ('user', 'exercise')
        verbose_name = _("Результат")
        verbose_name_plural = _("Результаты")

    def __str__(self):
        return f"{self.user} — {self.exercise} (балл: {self.score})"