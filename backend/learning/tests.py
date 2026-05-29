from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Role, Level, User, Course, Lesson, UserCourse,
    UserRole, Result, Exercise, TeacherCourse,
)


class BaseSetup(APITestCase):
    """Общие фикстуры: роли, уровень, пользователи, курсы с уроками."""

    def setUp(self):
        # Роли
        self.admin_role = Role.objects.create(name='admin')
        self.teacher_role = Role.objects.create(name='teacher')
        self.student_role = Role.objects.create(name='student')

        # Уровень
        self.level = Level.objects.create(name='A1', description='Beginner')

        # Пользователи
        self.admin = User.objects.create_user('admin_user', password='pass1234')
        UserRole.objects.create(user=self.admin, role=self.admin_role)

        self.teacher = User.objects.create_user('teacher_user', password='pass1234')
        UserRole.objects.create(user=self.teacher, role=self.teacher_role)

        self.student = User.objects.create_user('student_user', password='pass1234')
        UserRole.objects.create(user=self.student, role=self.student_role)

        self.other_student = User.objects.create_user('other_student', password='pass1234')
        UserRole.objects.create(user=self.other_student, role=self.student_role)

        # Курс 1 с уроком (попадает в PublishedCourseManager)
        self.course = Course.objects.create(title='Test Course', level=self.level)
        self.lesson = Lesson.objects.create(title='Lesson 1', course=self.course, order=1)

        # Курс 2 с уроком и заданием
        self.course2 = Course.objects.create(title='Test Course 2', level=self.level)
        self.lesson2 = Lesson.objects.create(title='Lesson 2', course=self.course2, order=1)
        self.exercise = Exercise.objects.create(
            lesson=self.lesson2, question='What is 2+2?', correct_answer='4', order=1,
        )


# ─── Аутентификация ──────────────────────────────────────────────────────────

class AuthTests(BaseSetup):

    def test_register_success(self):
        """Успешная регистрация создаёт пользователя и возвращает JWT-токены."""
        url = reverse('api_register')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'securepass1',
            'password_confirm': 'securepass1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_register_password_mismatch(self):
        """Несовпадение паролей при регистрации — ошибка 400."""
        url = reverse('api_register')
        data = {
            'username': 'baduser',
            'email': 'bad@test.com',
            'password': 'pass12345',
            'password_confirm': 'different',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Успешный вход возвращает access и refresh токены."""
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'admin_user', 'password': 'pass1234'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


# ─── Права доступа к курсам ───────────────────────────────────────────────────

class CoursePermissionTests(BaseSetup):

    def test_course_list_public(self):
        """Список курсов доступен без авторизации."""
        url = reverse('api_course_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_create_unauthenticated(self):
        """Создание курса без токена — ошибка 401."""
        url = reverse('api_course_create')
        response = self.client.post(url, {'title': 'Unauthorized', 'description': 'x'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_create_as_student_forbidden(self):
        """Студент не может создавать курсы — ошибка 403."""
        url = reverse('api_course_create')
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, {'title': 'Student Course'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_create_as_admin_success(self):
        """Администратор успешно создаёт курс — ответ 201."""
        url = reverse('api_course_create')
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, {'title': 'Admin Course', 'description': 'ok'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Admin Course')

    def test_course_create_as_teacher_success(self):
        """Преподаватель тоже может создавать курсы — ответ 201."""
        url = reverse('api_course_create')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, {'title': 'Teacher Course', 'description': 'ok'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_delete_as_teacher_forbidden(self):
        """Преподаватель не может удалять курсы (нужна роль admin) — ошибка 403."""
        url = reverse('api_course_delete', args=[self.course.pk])
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_delete_as_admin_success(self):
        """Администратор удаляет курс — ответ 204."""
        course = Course.objects.create(title='To Delete', level=self.level)
        Lesson.objects.create(title='L', course=course, order=1)
        url = reverse('api_course_delete', args=[course.pk])
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# ─── Валидация ────────────────────────────────────────────────────────────────

class ValidationTests(BaseSetup):

    def test_progress_over_100_invalid(self):
        """Обновление прогресса значением > 100 — ошибка 400."""
        enrollment = UserCourse.objects.create(user=self.student, course=self.course)
        url = reverse('api_enrollment_detail', args=[enrollment.pk])
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, {'progress': 150}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_progress_negative_invalid(self):
        """Обновление прогресса отрицательным значением — ошибка 400."""
        enrollment = UserCourse.objects.create(user=self.student, course=self.course)
        url = reverse('api_enrollment_detail', args=[enrollment.pk])
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, {'progress': -10}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_enrollment_invalid(self):
        """Повторная запись студента на тот же курс — ошибка 400."""
        UserCourse.objects.create(user=self.student, course=self.course)
        url = reverse('api_course_enrollments', args=[self.course.pk])
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            url, {'user': self.student.pk, 'progress': 0}, content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_requires_enrollment(self):
        """Студент без записи на курс не может сдать задание — ошибка 400."""
        url = reverse('api_results')
        self.client.force_authenticate(user=self.student)  # не записан на course2
        response = self.client.post(
            url,
            {'exercise': self.exercise.pk, 'user_answer': '4', 'score': 100},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_enrolled_student_success(self):
        """Записанный студент может сдать задание — ответ 201."""
        UserCourse.objects.create(user=self.student, course=self.course2)
        url = reverse('api_results')
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            url,
            {'exercise': self.exercise.pk, 'user_answer': '4', 'score': 90},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ─── Фильтрация ───────────────────────────────────────────────────────────────

class FilterTests(BaseSetup):

    def test_filter_by_level(self):
        """Фильтрация курсов по уровню возвращает только нужные курсы."""
        level2 = Level.objects.create(name='B1')
        other_course = Course.objects.create(title='B1 Course', level=level2)
        Lesson.objects.create(title='L', course=other_course, order=1)

        url = reverse('api_course_list')
        response = self.client.get(url, {'level': self.level.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [c['title'] for c in response.data]
        self.assertIn('Test Course', titles)
        self.assertNotIn('B1 Course', titles)

    def test_filter_by_created_after(self):
        """Фильтр created_after не ломает запрос и возвращает 200."""
        url = reverse('api_course_list')
        response = self.client.get(url, {'created_after': '2020-01-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ─── Поле is_enrolled ─────────────────────────────────────────────────────────

class IsEnrolledTests(BaseSetup):

    def test_is_enrolled_false_when_not_enrolled(self):
        """is_enrolled = False для студента, не записанного на курс."""
        url = reverse('api_course_list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_data = next(c for c in response.data if c['id'] == self.course.pk)
        self.assertFalse(course_data['is_enrolled'])

    def test_is_enrolled_true_when_enrolled(self):
        """is_enrolled = True для студента, записанного на курс."""
        UserCourse.objects.create(user=self.student, course=self.course)
        url = reverse('api_course_list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_data = next(c for c in response.data if c['id'] == self.course.pk)
        self.assertTrue(course_data['is_enrolled'])

    def test_is_enrolled_false_for_anonymous(self):
        """is_enrolled = False для анонимного пользователя."""
        url = reverse('api_course_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_data = next(c for c in response.data if c['id'] == self.course.pk)
        self.assertFalse(course_data['is_enrolled'])


# ─── Управление пользователями ────────────────────────────────────────────────

class UserAdminTests(BaseSetup):

    def test_admin_can_set_user_role(self):
        """Администратор успешно назначает роль пользователю."""
        url = reverse('api_user_set_role', args=[self.student.pk])
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, {'role': 'teacher'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'teacher')

    def test_student_cannot_set_role(self):
        """Студент не может изменить роль другого пользователя — ошибка 403."""
        url = reverse('api_user_set_role', args=[self.other_student.pk])
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            url, {'role': 'teacher'}, content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_list_requires_admin(self):
        """Список пользователей доступен только администратору."""
        url = reverse('api_users')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
