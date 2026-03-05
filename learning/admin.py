from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .pdf_utils import generate_course_pdf
from .models import (
    Role, Level, User, UserRole,
    Course, TeacherCourse, UserCourse,
    Lesson, ExerciseType, Exercise, Result
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name', 'description')
    ordering = ('name',)

    @admin.display(description=_("Описание"))
    def description_short(self, obj):
        return (obj.description[:60] + "...") if len(obj.description) > 60 else obj.description or "-"
    

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name', 'description')
    ordering = ('name',)

    @admin.display(description=_("Описание"))
    def description_short(self, obj):
        return (obj.description[:60] + "...") if len(obj.description) > 60 else obj.description or "-"
    

class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1
    verbose_name = _("Роль")
    verbose_name_plural = _("Роли пользователя")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'get_roles_display', 'level', 'is_active', 'date_joined')
    list_display_links = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'level', 'roles')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    raw_id_fields = ('level',)
    inlines = [UserRoleInline]

    fieldsets = UserAdmin.fieldsets + (
        (_('Дополнительно'), {'fields': ('level',)}),
    )

    @admin.display(description=_("Роли"))
    def get_roles_display(self, obj):
        roles = [r.name for r in obj.roles.all()]
        return ", ".join(roles) if roles else "-"


class UserCourseInline(admin.TabularInline):
    # Список учеников, записанных на курс.
    model = UserCourse
    extra = 0
    raw_id_fields = ('user', 'teacher')
    fields = ('user', 'teacher', 'enrolled_at', 'progress')
    readonly_fields = ('enrolled_at',)

class TeacherCourseInline(admin.TabularInline):
    # Список преподавателей, прикреплённых к курсу.
    model = TeacherCourse
    extra = 1
    raw_id_fields = ('teacher',)
    fields = ('teacher',)

class LessonInline(admin.TabularInline):
    # Уроки внутри курса.
    model = Lesson
    extra = 1
    fields = ('order', 'title', 'description_short')
    readonly_fields = ('description_short',)
    ordering = ('order',)
    show_change_link = True

    @admin.display(description=_("Описание (кратко)"))
    def description_short(self, obj):
        return (obj.description[:80] + "...") if len(obj.description) > 80 else obj.description or "-"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'get_teachers_count', 'get_students_count', 'get_lessons_count', 'created_at')
    list_display_links = ('title',)
    list_filter = ('level', 'created_at')
    search_fields = ('title', 'description', 'level__name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('level',)
    readonly_fields = ('created_at',)
    actions = ['export_as_pdf']
    inlines = [LessonInline, TeacherCourseInline, UserCourseInline]

    fieldsets = (
        (None, {'fields': ('title', 'level', 'description')}),
        (_('Даты'), {'fields': ('created_at',)}),
    )
    @admin.action(description='Скачать PDF')
    def export_as_pdf(self, request, queryset):
        course = queryset.first()
        return generate_course_pdf(course)

    @admin.display(description=_("Преподавателей"))
    def get_teachers_count(self, obj):
        cnt = obj.teachers.count()
        return cnt if cnt > 0 else format_html('<span style="color: gray;">—</span>')

    @admin.display(description=_("Учеников"))
    def get_students_count(self, obj):
        return obj.usercourse_set.count()

    @admin.display(description=_("Уроков"))
    def get_lessons_count(self, obj):
        return obj.lessons.count()


class ExerciseInline(admin.TabularInline):
    # Задания внутри урока.
    model = Exercise
    extra = 1
    fields = ('order', 'exercise_type', 'question_short', 'correct_answer_short')
    readonly_fields = ('question_short', 'correct_answer_short')
    ordering = ('order',)
    show_change_link = True

    @admin.display(description=_("Вопрос (кратко)"))
    def question_short(self, obj):
        return (obj.question[:60] + "...") if len(obj.question) > 60 else obj.question or "-"

    @admin.display(description=_("Ответ (кратко)"))
    def correct_answer_short(self, obj):
        return (obj.correct_answer[:40] + "...") if len(obj.correct_answer) > 40 else obj.correct_answer or "-"
    

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'get_exercises_count')
    list_display_links = ('title',)
    list_filter = ('course', 'course__level')
    search_fields = ('title', 'description', 'course__title')
    raw_id_fields = ('course',)
    ordering = ('course', 'order')
    inlines = [ExerciseInline]

    @admin.display(description=_("Заданий"))
    def get_exercises_count(self, obj):
        return obj.exercises.count()


@admin.register(ExerciseType)
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name',)

    @admin.display(description=_("Описание"))
    def description_short(self, obj):
        return (obj.description[:60] + "...") if len(obj.description) > 60 else obj.description or "-"
    

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('question_short', 'lesson', 'order', 'exercise_type')
    list_display_links = ('question_short',)
    list_filter = ('exercise_type', 'lesson__course', 'lesson__course__level')
    search_fields = ('question', 'correct_answer', 'lesson__title', 'lesson__course__title')
    raw_id_fields = ('lesson',)
    ordering = ('lesson', 'order')

    @admin.display(description=_("Вопрос"))
    def question_short(self, obj):
        return (obj.question[:70] + "...") if len(obj.question) > 70 else obj.question


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise_short', 'colored_score', 'completed_at')
    list_display_links = ('user',)
    list_filter = ('completed_at', 'score', 'exercise__lesson__course')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'exercise__question')
    date_hierarchy = 'completed_at'
    raw_id_fields = ('user', 'exercise')
    readonly_fields = ('completed_at',)

    @admin.display(description=_("Задание"))
    def exercise_short(self, obj):
        q = obj.exercise.question
        return (q[:50] + "...") if len(q) > 50 else q

    @admin.display(description=_("Балл"), ordering='score')
    def colored_score(self, obj):
        if obj.score >= 80:
            color = 'green'
        elif obj.score <= 30:
            color = 'red'
        else:
            color = 'orange'
        return format_html('<b style="color: {};">{}</b>', color, obj.score)


@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'teacher', 'progress', 'enrolled_at')
    list_filter = ('course', 'course__level')
    search_fields = ('user__username', 'course__title')
    raw_id_fields = ('user', 'course', 'teacher')
    readonly_fields = ('enrolled_at',)


@admin.register(TeacherCourse)
class TeacherCourseAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'course')
    search_fields = ('teacher__username', 'course__title')
    raw_id_fields = ('teacher', 'course')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role__name')
    raw_id_fields = ('user',)
