# 🎓 ENGLOBE — Онлайн-школа английского языка

Веб-приложение для онлайн-школы английского языка. Разработано на Django REST Framework + React + TypeScript.

---

## Стек технологий

**Backend**
- Python 3.11
- Django 5.2
- Django REST Framework
- SimpleJWT — аутентификация по JWT токенам
- PostgreSQL

**Frontend**
- React 18 + TypeScript
- Vite
- React Router v6
- Axios
- SCSS Modules

---

## Структура проекта

```
english-school-project/
├── backend/
│   ├── core/                  # Настройки Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── learning/              # Основное приложение
│   │   ├── models.py          
│   │   ├── serializers.py     
│   │   ├── api_views.py       # REST API views
│   │   ├── admin.py           
│   │   ├── urls.py           
│   │   └── pdf_utils.py
│   ├── media/                 # Загружаемые файлы
│   ├── manage.py
│   └── .env
│
└── frontend/
    └── src/
        ├── api/
        │   └── axios.ts
        ├── components/
        │   ├── Button/
        │   ├── CourseCard/        
        │   ├── Footer/
        │   ├── Layout/           
        │   ├── Navbar/
        │   ├── TeacherCard/
        │   └── TeacherSlider/
        ├── context/
        │   ├── AuthContext.ts     # Тип контекста авторизации
        │   ├── AuthProvider.tsx   # Провайдер (login, register, logout)
        │   └── useAuth.ts         
        ├── pages/
        │   ├── HomePage/          # Главная страница
        │   ├── CoursesPage/       # Список всех курсов
        │   ├── CoursePage/        # Детальная страница курса
        │   ├── CourseEditPage/    # Создание / редактирование курса
        │   ├── LoginPage/         # Вход
        │   ├── RegisterPage/      # Регистрация
        │   └── UsersAdminPage/    # Управление пользователями
        ├── styles/                # Глобальные стили, переменные
        └── types/
            └── index.ts           # TypeScript типы
```

---

## Модели базы данных

| Модель | Описание |
|---|---|
| `User` | Пользователь (расширяет AbstractUser), имеет уровень и роли |
| `Role` | Роль пользователя: `student`, `teacher`, `admin` |
| `Level` | Уровень языка: A1, A2, B1, B2, C1, C2 |
| `UserRole` | Связь пользователь ↔ роль |
| `Course` | Курс с названием, описанием, уровнем и обложкой |
| `TeacherCourse` | Связь преподаватель ↔ курс |
| `UserCourse` | Запись студента на курс (прогресс, статус, доступ) |
| `Lesson` | Урок внутри курса |
| `ExerciseType` | Тип задания |
| `Exercise` | Задание внутри урока |
| `Result` | Результат выполнения задания студентом |

---

## API Endpoints

| Метод | URL | Описание |
|---|---|---|
| POST | `/api/auth/login/` | Получить JWT токены |
| POST | `/api/auth/refresh/` | Обновить access токен |
| POST | `/api/auth/register/` | Регистрация |
| GET, POST | `/api/users/` | Пользователи (фильтр `?role=teacher`) |
| POST | `/api/users/<id>/role/` | Назначить роль |
| GET | `/api/courses/` | Список курсов |
| GET | `/api/courses/<id>/` | Детали курса |
| POST | `/api/courses/create/` | Создать курс |
| PATCH | `/api/courses/<id>/update/` | Обновить курс |
| DELETE | `/api/courses/<id>/delete/` | Удалить курс |
| GET, POST | `/api/courses/<id>/lessons/` | Уроки курса |
| PATCH, DELETE | `/api/lessons/<id>/` | Урок |
| GET, POST | `/api/courses/<id>/teachers/` | Преподаватели курса |
| DELETE | `/api/courses/<id>/teachers/<user_id>/` | Снять преподавателя |
| GET, POST | `/api/courses/<id>/enrollments/` | Записи на курс |
| PATCH, DELETE | `/api/enrollments/<id>/` | Запись |
| GET | `/api/home/` | Данные главной страницы |
| GET | `/api/levels/` | Уровни языка |
| GET | `/api/my-courses/` | Мои курсы |

---

## Установка и запуск

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Создай файл `.env` в папке `backend/`:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=englobe
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Фронтенд запускается на `http://localhost:5173`, бэкенд на `http://localhost:8000`.

Vite проксирует запросы `/api` на бэкенд — настройка в `vite.config.js`.

---

## Аутентификация

Используется JWT (JSON Web Tokens) через `djangorestframework-simplejwt`.

- **Access токен** — короткоживущий, передаётся в заголовке `Authorization: Bearer <token>` при каждом запросе
- **Refresh токен** — долгоживущий, используется для автоматического обновления access токена
- Оба токена хранятся в `localStorage`
- При истечении access токена Axios автоматически обновляет его через интерцептор

---

## Функциональность

- Регистрация и вход с JWT авторизацией
- Просмотр каталога курсов с поиском и фильтрацией
- Детальная страница курса: уроки, задания, преподаватели
- Создание, редактирование и удаление курсов
- Управление уроками и преподавателями курса прямо на странице редактирования
- Запись студентов на курсы
- Управление ролями пользователей (student / teacher)
- Слайдер преподавателей на главной странице
- Статистика школы: количество курсов, уроков, студентов, средний балл

---

## Админка Django

Доступна по адресу `http://localhost:8000/admin/`

Возможности:
- Управление пользователями и ролями
- CRUD для курсов, уроков, заданий
- Просмотр результатов выполнения заданий
- Экспорт курса в PDF
- Инлайн-редактирование связанных объектов