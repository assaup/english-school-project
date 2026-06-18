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
        self.admin_role = Role.objects.create(name='admin')
        self.teacher_role = Role.objects.create(name='teacher')
        self.student_role = Role.objects.create(name='student')

        self.level = Level.objects.create(name='A1', description='Beginner')

        self.admin = User.objects.create_user('admin_user', password='pass1234')
        UserRole.objects.create(user=self.admin, role=self.admin_role)

        self.teacher = User.objects.create_user('teacher_user', password='pass1234')
        UserRole.objects.create(user=self.teacher, role=self.teacher_role)

        self.student = User.objects.create_user('student_user', password='pass1234')
        UserRole.objects.create(user=self.student, role=self.student_role)

        self.other_student = User.objects.create_user('other_student', password='pass1234')
        UserRole.objects.create(user=self.other_student, role=self.student_role)

        self.course = Course.objects.create(title='Test Course', level=self.level)
        self.lesson = Lesson.objects.create(title='Lesson 1', course=self.course, order=1)

        self.course2 = Course.objects.create(title='Test Course 2', level=self.level)
        self.lesson2 = Lesson.objects.create(title='Lesson 2', course=self.course2, order=1)
        self.exercise = Exercise.objects.create(
            lesson=self.lesson2, question='What is 2+2?', correct_answer='4', order=1,
        )


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


class CoursePermissionTests(BaseSetup):

    def test_course_list_public(self):
        """Список курсов доступен без авторизации."""
        url = reverse('api_course_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_create_unauthenticated(self):
        """Создание курса без токена — ошибка 401."""
        url = reverse('api_course_create')
        response = self.client.post(url, {'title': 'Unauthorized'})
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

    def test_course_delete_as_admin_success(self):
        """Администратор удаляет курс — ответ 204."""
        course = Course.objects.create(title='To Delete', level=self.level)
        Lesson.objects.create(title='L', course=course, order=1)
        url = reverse('api_course_delete', args=[course.pk])
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ValidationTests(BaseSetup):

    def test_progress_over_100_invalid(self):
        """Обновление прогресса значением > 100 — ошибка 400."""
        enrollment = UserCourse.objects.create(user=self.student, course=self.course)
        url = reverse('api_enrollment_detail', args=[enrollment.pk])
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, {'progress': 150}, content_type='application/json')
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


class IsEnrolledTests(BaseSetup):

    def test_is_enrolled_false_when_not_enrolled(self):
        """is_enrolled = False для студента, не записанного на курс."""
        url = reverse('api_course_list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        course_data = next(c for c in response.data if c['id'] == self.course.pk)
        self.assertFalse(course_data['is_enrolled'])

    def test_is_enrolled_true_when_enrolled(self):
        """is_enrolled = True для студента, записанного на курс."""
        UserCourse.objects.create(user=self.student, course=self.course)
        url = reverse('api_course_list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        course_data = next(c for c in response.data if c['id'] == self.course.pk)
        self.assertTrue(course_data['is_enrolled'])