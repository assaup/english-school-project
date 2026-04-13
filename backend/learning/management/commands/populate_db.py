from django.core.management.base import BaseCommand
from faker import Faker
import random
from backend.learning.models import (
    Role, Level, User, UserRole,
    Course, TeacherCourse, UserCourse,
    Lesson, Exercise, ExerciseType, Result
)
from django.utils import timezone
from datetime import timedelta

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        self.create_roles()
        self.create_levels()
        self.create_users(20)
        self.assign_user_roles()
        self.create_exercise_types()
        self.create_courses(10)
        self.assign_teachers()
        self.create_user_courses()
        self.create_lessons()
        self.create_exercises()
        self.create_results(100)
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))

    def create_roles(self):
        self.stdout.write('Создаём роли...')
        roles = ['student', 'teacher', 'admin']
        for role_name in roles:
            Role.objects.get_or_create(name=role_name, defaults={'description': fake.sentence()})

    def create_levels(self):
        self.stdout.write('Создаём уровни...')
        levels = ['A1', 'A2', 'B1', 'B2', 'C1']
        for level_name in levels:
            Level.objects.get_or_create(name=level_name, defaults={'description': fake.sentence()})

    def create_users(self, number):
        self.stdout.write(f'Создаём {number} пользователей...')
        levels = list(Level.objects.all())
        for _ in range(number):
            User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='samir123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                level=random.choice(levels)
            )

    def assign_user_roles(self):
        self.stdout.write('Назначаем роли пользователям...')
        users = list(User.objects.all())
        roles = list(Role.objects.all())

        student_role = Role.objects.get(name='student')
        teacher_role = Role.objects.get(name='teacher')

        for i, user in enumerate(users):
            if i < 4:
                UserRole.objects.get_or_create(user=user, role=teacher_role)
            else:
                UserRole.objects.get_or_create(user=user, role=student_role)

        for user in users[4:]:
            extra_roles = random.sample(roles, k=random.randint(1, 2))
            for role in extra_roles:
                UserRole.objects.get_or_create(user=user, role=role)

    def create_exercise_types(self):
        self.stdout.write('Создаём типы заданий...')
        types = [
            ('Выбор ответа', 'Выберите правильный вариант из предложенных'),
            ('Заполни пропуск', 'Вставьте нужное слово в предложение'),
            ('Перевод', 'Переведите предложение на английский язык'),
            ('Аудирование', 'Прослушайте и ответьте на вопрос'),
        ]
        for name, description in types:
            ExerciseType.objects.get_or_create(name=name, defaults={'description': description})

    def create_courses(self, number):
        self.stdout.write(f'Создаём {number} курсов...')
        levels = list(Level.objects.all())
        
        course_titles = [
            'Английский для начинающих',
            'Разговорный английский',
            'Деловой английский',
            'Английский для путешествий',
            'Грамматика английского языка',
            'Английский для IT-специалистов',
            'Подготовка к IELTS',
            'Подготовка к TOEFL',
            'Английский для детей',
            'Английский для медиков',
            'Американский английский',
            'Британский английский',
        ]
        
        for i in range(number):
            Course.objects.create(
                title=course_titles[i % len(course_titles)],
                description=fake.paragraph(),
                level=random.choice(levels),
            )

    def assign_teachers(self):
        self.stdout.write('Назначаем преподавателей на курсы...')
        teacher_role = Role.objects.get(name='teacher')
        teacher_ids = UserRole.objects.filter(role=teacher_role).values_list('user_id', flat=True)
        teachers = list(User.objects.filter(id__in=teacher_ids))

        if not teachers:
            self.stdout.write(self.style.WARNING('Нет учителей! Пропускаем назначение.'))
            return

        courses = list(Course.objects.all())
        for course in courses:
            assigned = random.sample(teachers, k=min(random.randint(1, 2), len(teachers)))
            for teacher in assigned:
                TeacherCourse.objects.get_or_create(teacher=teacher, course=course)

    def create_user_courses(self):
        self.stdout.write('Записываем учеников на курсы...')
        student_role = Role.objects.get(name='student')
        student_ids = UserRole.objects.filter(role=student_role).values_list('user_id', flat=True)
        students = list(User.objects.filter(id__in=student_ids))
        courses = list(Course.objects.all())
        statuses = [s[0] for s in UserCourse.Status.choices]

        for student in students:
            enrolled_courses = random.sample(courses, k=min(random.randint(2, 4), len(courses)))
            for course in enrolled_courses:
                teacher_course = TeacherCourse.objects.filter(course=course).first()
                teacher = teacher_course.teacher if teacher_course else None

                access_until = timezone.now() + timedelta(days=random.randint(-30, 180))

                UserCourse.objects.get_or_create(
                    user=student,
                    course=course,
                    defaults={
                        'teacher': teacher,
                        'status': random.choice(statuses),
                        'progress': round(random.uniform(0, 100), 1),
                        'access_until': access_until,
                    }
                )

    def create_lessons(self):
        self.stdout.write('Создаём уроки...')
        courses = list(Course.objects.all())
        lesson_topics = [
            'Приветствие и знакомство', 'Числа и счёт', 'Цвета и формы',
            'Семья и родственники', 'Еда и напитки', 'Время и дата',
            'Погода и сезоны', 'Путешествия', 'Работа и профессии',
            'Покупки и магазины', 'Здоровье и спорт', 'Природа и животные',
        ]
        for course in courses:
            # В каждом курсе от 3 до 6 уроков
            num_lessons = random.randint(3, 6)
            topics = random.sample(lesson_topics, k=min(num_lessons, len(lesson_topics)))
            for order, topic in enumerate(topics, start=1):
                Lesson.objects.create(
                    title=topic,
                    description=fake.paragraph(),
                    order=order,
                    course=course,
                )

    def create_exercises(self):
        self.stdout.write('Создаём задания...')
        lessons = list(Lesson.objects.all())
        exercise_types = list(ExerciseType.objects.all())

        sample_questions = [
            'Переведите слово "apple"',
            'Выберите правильный артикль: ___ cat',
            'Составьте предложение из слов: is / she / happy',
            'Вставьте глагол в нужной форме: She ___ (go) to school',
            'Как по-английски "привет"?',
            'Переведите: "I like reading books"',
            'Напишите множественное число: child',
            'Выберите правильный предлог: He is good ___ math',
        ]

        for lesson in lessons:
            num_exercises = random.randint(3, 6)
            for order in range(1, num_exercises + 1):
                Exercise.objects.create(
                    question=random.choice(sample_questions),
                    correct_answer=fake.word(),
                    exercise_type=random.choice(exercise_types) if exercise_types else None,
                    lesson=lesson,
                    order=order,
                )

    def create_results(self, number):
        self.stdout.write(f'Создаём {number} результатов...')
        student_role = Role.objects.get(name='student')
        student_ids = UserRole.objects.filter(role=student_role).values_list('user_id', flat=True)
        students = list(User.objects.filter(id__in=student_ids))
        exercises = list(Exercise.objects.all())

        if not students or not exercises:
            self.stdout.write(self.style.WARNING('Нет студентов или заданий, пропускаем результаты.'))
            return

        created = 0
        attempts = 0
        # Пробуем создать нужное количество уникальных результатов
        while created < number and attempts < number * 3:
            attempts += 1
            student = random.choice(students)
            exercise = random.choice(exercises)
            _, was_created = Result.objects.get_or_create(
                user=student,
                exercise=exercise,
                defaults={
                    'user_answer': fake.sentence(),
                    'score': random.randint(0, 100),
                }
            )
            if was_created:
                created += 1

        self.stdout.write(f'  Создано результатов: {created}')