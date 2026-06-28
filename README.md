# Foodgram — сервис публикации рецептов

[![Main foodgram workflow](https://github.com/StasKharitonov/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/StasKharitonov/foodgram/actions/workflows/main.yml)
[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red.svg)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-Containers-blue.svg)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-purple.svg)](https://github.com/features/actions)

## Описание проекта

Foodgram — веб-сервис для публикации и хранения рецептов. Пользователи могут регистрироваться, создавать рецепты, добавлять их в избранное и список покупок, подписываться на авторов и скачивать список ингредиентов.

**Сайт проекта:** https://acidfoodgram.ddns.net

**Документация API:** https://acidfoodgram.ddns.net/api/docs/

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| **Backend** | Django 5.1, Django REST Framework 3.15, Djoser |
| **Frontend** | React 17 |
| **База данных** | PostgreSQL 13 |
| **Веб-сервер** | Nginx |
| **Контейнеризация** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Развёртывание** | Ubuntu (Yandex Cloud) |

## Архитектура

Проект состоит из четырёх контейнеров:

- **db** — PostgreSQL
- **backend** — Django + Gunicorn
- **frontend** — React-сборка
- **gateway** — Nginx (проксирует API, админку, статику и медиа)

## Как развернуть проект

### Локальный запуск через Docker

```bash
# 1. Клонировать репозиторий
git clone https://github.com/StasKharitonov/foodgram.git
cd foodgram

# 2. Создать файл .env в корне проекта
```

Пример `.env`:

```env
POSTGRES_USER=django_user
POSTGRES_PASSWORD=your-password
POSTGRES_DB=django

DB_HOST=db
DB_PORT=5432
```

```bash
# 3. Запустить контейнеры
sudo docker compose up -d

# 4. Применить миграции
sudo docker compose exec backend python manage.py migrate

# 5. Загрузить теги и ингредиенты
sudo docker compose exec backend python manage.py load_tags
sudo docker compose exec backend python manage.py load_csv

# 6. Собрать статику Django
sudo docker compose exec backend python manage.py collectstatic --noinput
```

Приложение будет доступно по адресу: http://localhost:7000

### Локальная разработка (infra)

Для разработки фронтенда и API без production-образов можно использовать каталог `infra/`:

```bash
cd infra
docker compose up
```

- Фронтенд: http://localhost
- Документация API: http://localhost/api/docs/

## CI/CD

При push в ветку `main` GitHub Actions:

1. Запускает тесты backend (flake8, Django) и frontend
2. Собирает и публикует образы в Docker Hub
3. Деплоит проект на сервер
4. Выполняет `migrate`, `collectstatic`, `load_tags`, `load_csv`

Workflow можно запустить вручную: **Actions** → **Main foodgram workflow** → **Run workflow**.

## Автор

**Станислав Харитонов**

- GitHub: https://github.com/StasKharitonov
- Email: youngstarmoscow@gmail.com
