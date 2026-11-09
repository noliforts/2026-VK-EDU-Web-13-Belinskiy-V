# Qurilka — форум вопросов и ответов

Учебный проект VK Education (Web, ДЗ2): сайт вопросов и ответов в стиле старых форумов на Django. Views пока отдают данные-заглушки («рыбу»), базы данных для вопросов ещё нет.

## Как запустить

### Локально (venv)

Нужен Python 3.12+.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # настройки (SECRET_KEY, DEBUG, БД) лежат в .env, его нет в git
python manage.py migrate
python manage.py runserver
```

### Через Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

В обоих случаях сайт доступен по адресу http://127.0.0.1:8000/.

## Структура

```
application/     настройки проекта (settings.py, urls.py)
core/            вход, регистрация, профиль, правила, помощь
questions/       списки вопросов, страница вопроса, создание вопроса
templates/       общий base.html и подшаблоны (includes/)
static/          сюда collectstatic собирает статику (в git не хранится)
media/           загруженные пользователями файлы (в git не хранится)
```

Шаблоны и статика приложений лежат в `core/templates/core/`, `core/static/core/`, `questions/templates/questions/`.

## Страницы

| URL | Имя маршрута | Страница |
|---|---|---|
| `/` | `index` | новые вопросы |
| `/hot/` | `hot` | горячие вопросы |
| `/tag/<тег>/` | `tag` | вопросы по тегу |
| `/question/<id>/` | `question` | вопрос со списком ответов |
| `/ask/` | `ask` | создание вопроса |
| `/login/` | `login` | вход |
| `/signup/` | `signup` | регистрация |
| `/profile/` | `profile` | настройки профиля |
| `/rules/` | `rules` | правила |
| `/help/` | `help` | помощь |

## Пагинация

Функция `paginate(objects_list, request, per_page=10)` лежит в `core/utils.py`. Шаблон пагинатора: `templates/includes/paginator.html`. Если параметр `?page=` не число или страница не существует, показывается первая страница.

## Шапка: авторизованный и неавторизованный вид

Шапка одна (`templates/includes/header.html`), её вид переключается проверкой `{% if user.is_authenticated %}`. Переменную `user` Django сама передаёт во все шаблоны. Чтобы увидеть авторизованный вид, нужно войти через `/admin/` (предварительно `python manage.py migrate` и `python manage.py createsuperuser`).

| Вид | Когда показывается | Что в шапке |
|---|---|---|
| авторизованный | пользователь вошёл | поиск, кнопка «Задать вопрос», аватар, имя, «настройки», «выход» |
| неавторизованный | пользователь не вошёл | поиск, «Вход», «Регистрация» (без кнопки «Задать вопрос») |
