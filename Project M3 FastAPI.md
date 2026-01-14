# Техническое задание: Интернет-магазин на FastAPI

## 1. Введение и цель

Вы — разработчик на первой работе. Нужно трансформировать готовый статический HTML/CSS дизайн в полноценное интернет-магазин приложение на FastAPI. Проект должен содержать:

- Веб-интерфейс (FastAPI, Jinja2 шаблоны, сессии)
- REST API для внешних клиентов (FastAPI, JWT)
- (Опционально) GraphQL для аналитики как дополнительное улучшение
- Инфраструктуру: PostgreSQL, Docker
- Качество кода: типизация, линтеры, тесты, документация

Цель: показать понимание FastAPI, работы с базой данных (SQLAlchemy), архитектурных практик, качества кода и деплоя.

HTML Template - https://github.com/MagicCodeGit/Hop-and-Barley.git

---

## 2. Общие принципы

- **Веб-интерфейс** (пользователи через браузер) использует **session-based** аутентификацию (через cookies/сессии FastAPI).
- **Внешние API** используют **JWT** для авторизации.
- GraphQL (если реализуется) доступен через **один эндпоинт** `/graphql/`.
- Структура проекта примерная — допускаются вариации, но должна быть логичная модульность.
- **Инфраструктура:** обязательное использование PostgreSQL, всё поднимается через Docker Compose.
- Альтернативные менеджеры зависимостей (`poetry`, `uv`) приветствуются как бонус.
- Использование **асинхронности** (async/await) для работы с БД и внешними сервисами.

---

## 3. Функциональные блоки

### 3.1. Каталог товаров и поиск (`/` и `/products/`)

**Функциональность:**

- Список товаров с пагинацией
- Фильтрация по категории, диапазону цен
- Поиск по названию и описанию
- Сортировка (по цене, популярности, новизне)

**Темы:** FastAPI роутеры, Jinja2 шаблоны, SQLAlchemy ORM, оптимизация запросов (select_related, prefetch_related эквиваленты)

**Реализация:**
- Роутер: `app/web/router.py` или `app/api/v1/endpoints/products.py`
- Шаблон: `app/templates/home.html` (Jinja2)
- Использование query parameters для фильтров: `?category=hops&min_price=5&max_price=10&search=citra&sort=price_asc`

### 3.2. Страница товара (`/product/{slug}/`)

- Детальная информация (название, описание, цена, изображения, рейтинг)
- Отзывы с рейтингами (1–5), возможность оставить отзыв (только после покупки — проверка)
- Кнопка "Добавить в корзину", выбор количества

**Темы:** Path parameters, формы (FastAPI Form), ORM, валидация (Pydantic)

**Реализация:**
- Роутер: `/product/{slug}` с использованием path parameter
- Шаблон: `app/templates/product-detail.html` (динамический, не статический)
- Проверка прав на отзыв через проверку заказов пользователя

### 3.3. Корзина (`/cart/`)

- Просмотр содержимого корзины
- Добавление, удаление, изменение количества
- Подсчёт итоговой стоимости, учёт остатка
- Хранение в сессии (FastAPI SessionMiddleware)
- Проверка наличия товара

**Темы:** FastAPI Sessions, Flash messages (через templates), бизнес-логика

**Реализация:**
- Использование `SessionMiddleware` из `starlette.middleware.sessions`
- Роутеры: GET `/cart/`, POST `/cart/add/`, POST `/cart/update/`, POST `/cart/remove/`
- Шаблон: `app/templates/cart.html`

### 3.4. Оформление заказа (`/checkout/`)

- Форма для данных доставки/контакта
- Выбор способа оплаты (мок/эмуляция)
- Создание заказа
- Email-уведомления пользователю и администратору
- Обработка ошибок и валидация

**Темы:** FastAPI Form, email (aiosmtplib или FastAPI Mail), транзакции (SQLAlchemy)

**Реализация:**
- Роутер: GET `/checkout/` (форма), POST `/checkout/` (создание заказа)
- Шаблон: `app/templates/checkout.html`
- Использование транзакций для атомарности создания заказа

### 3.5. Личный кабинет (`/account/`)

- Регистрация, вход/выход (session auth)
- История заказов (с фильтрацией)
- Редактирование профиля
- Смена пароля
- (Опционально) управление адресами доставки

**Темы:** Аутентификация (FastAPI Security), ORM, формы, доступ (Dependencies)

**Реализация:**
- Роутеры: `/register/`, `/login/`, `/logout/`, `/account/`, `/account/orders/`
- Шаблоны: `app/templates/register.html`, `app/templates/login.html`, `app/templates/account.html`
- Использование `Depends` для проверки аутентификации

### 3.6. Админ-панель (`/admin/`)

- Управление товарами, категориями, заказами, отзывами, пользователями
- Аналитика: агрегаты, аннотации (выручка, топ-продукты, количество заказов)
- Поиск, фильтры, кастомные action'ы
- Права доступа

**Темы:** Админка (кастомная или использование библиотек), агрегаты SQLAlchemy, кастомизация

**Реализация:**
- Роутеры: `/admin/`, `/admin/products/`, `/admin/orders/`, `/admin/analytics/`
- Шаблоны: `app/templates/admin/dashboard.html`, `app/templates/admin/products.html`
- Использование SQLAlchemy агрегатных функций (func.sum, func.count)

### 3.7. REST API (`/api/v1/`)

Ресурсы и действия (пример):

| Ресурс       | Действие          | URL-шаблон                    | HTTP метод(ы)            | Описание                               | Авторизация    |
|--------------|-------------------|-------------------------------|--------------------------|----------------------------------------|----------------|
| Товары       | Список            | `/api/v1/products/`           | GET                      | Пагинация, фильтрация, поиск           | Необязательно  |
| Товары       | Деталь            | `/api/v1/products/{id}/`      | GET                      | Информация о товаре                    | Необязательно  |
| Заказы       | Создание          | `/api/v1/orders/`              | POST                     | Создание заказа (на основе корзины)    | JWT            |
| Заказы       | Список своих      | `/api/v1/orders/`              | GET                      | Список заказов текущего пользователя   | JWT            |
| Заказы       | Деталь            | `/api/v1/orders/{id}/`         | GET                      | Детальная информация (только свой)     | JWT            |
| Заказы       | Обновление/отмена | `/api/v1/orders/{id}/`         | PATCH/PUT/DELETE         | Изменение статуса/отмена (по правилам) | JWT            |
| Пользователи | Регистрация       | `/api/v1/users/register/`      | POST                     | Создать аккаунт                        | Нет            |
| Пользователи | Вход (JWT)        | `/api/v1/users/login/`         | POST                     | Получить access/refresh токены         | Нет            |
| Корзина      | Управление        | `/api/v1/cart/`                | GET, POST, PATCH, DELETE | Содержимое корзины                     | JWT или сессия |
| Отзывы       | Добавить/просмотр | `/api/v1/products/{id}/reviews/` | GET, POST                | Список и отправка отзыва               | JWT            |

- JWT: access + refresh, обновление.
- Права: пользователь видит/меняет только свои данные.
- Использование Pydantic схем для валидации запросов/ответов.

**Темы:** FastAPI роутеры, Pydantic схемы, пагинация, permissions (Depends)

**Реализация:**
- Структура: `app/api/v1/endpoints/products.py`, `app/api/v1/endpoints/orders.py`, и т.д.
- Схемы: `app/schemas/product.py`, `app/schemas/order.py`
- Использование `python-jose` для JWT, `passlib` для хеширования паролей

### 3.8. Документация API

- Swagger/OpenAPI для REST API (автоматически доступна на `/docs/`)
- ReDoc альтернатива (автоматически на `/redoc/`)
- Примеры запросов, схемы, авторизация

**Темы:** Автоматическая документация FastAPI (встроенная)

**Реализация:**
- FastAPI автоматически генерирует OpenAPI схему
- Дополнительные описания через docstrings и Pydantic Field descriptions

### 3.9. (Бонусно) GraphQL

- Один эндпоинт `/graphql/`
- Аналитические запросы:
    - Заказы: выручка, количество, средний чек, тренды
    - Продукты: популярные, остатки
    - Пользователи: активность, повторные покупки

**Темы:** Strawberry GraphQL или Ariadne, резолверы, авторизация в GraphQL

> Примечание: GraphQL — бонус. Можно заменить на другие улучшения (например, расширенные тесты, CI/CD и т.п.).

---

## 4. Структура данных (База данных)

### Category

- `id` (PK, Integer)
- `name` (String)
- `slug` (String, unique)
- `parent_id` (ForeignKey to Category, nullable) — для вложенности
- `created_at` (DateTime)
- `updated_at` (DateTime)

**SQLAlchemy модель:**
```python
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Product

- `id` (PK, Integer)
- `name` (String)
- `slug` (String, unique)
- `description` (Text)
- `price` (Numeric/Decimal)
- `category_id` (ForeignKey to Category)
- `image` (String — путь к файлу)
- `is_active` (Boolean)
- `stock` (Integer)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**SQLAlchemy модель:**
```python
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    image = Column(String)
    is_active = Column(Boolean, default=True)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### User

- `id` (PK, Integer)
- `email` (String, unique)
- `username` (String, unique)
- `hashed_password` (String)
- `is_active` (Boolean)
- `is_superuser` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Order

- `id` (PK, Integer)
- `user_id` (ForeignKey to User)
- `status` (String: pending, paid, shipped, delivered, cancelled)
- `total_price` (Numeric/Decimal)
- `shipping_address` (Text / отдельная модель)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### OrderItem

- `id` (PK, Integer)
- `order_id` (ForeignKey to Order)
- `product_id` (ForeignKey to Product)
- `quantity` (Integer)
- `price` (Numeric/Decimal) — snapshot цены на момент заказа

### Review

- `id` (PK, Integer)
- `product_id` (ForeignKey to Product)
- `user_id` (ForeignKey to User)
- `rating` (Integer 1–5)
- `comment` (Text)
- `created_at` (DateTime)

*Дополнительно:* Address, Payment и др. по необходимости.

---

## 5. Примерная архитектура проекта

```
/web-shop-fastapi-template/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # Роутер для API v1
│   │       └── endpoints/
│   │           ├── products.py     # API эндпоинты для товаров
│   │           ├── orders.py       # API эндпоинты для заказов
│   │           ├── users.py        # API эндпоинты для пользователей
│   │           ├── cart.py         # API эндпоинты для корзины
│   │           └── reviews.py      # API эндпоинты для отзывов
│   ├── core/
│   │   ├── config.py               # Настройки (Pydantic Settings)
│   │   ├── database.py             # SQLAlchemy engine, session
│   │   ├── security.py             # JWT, хеширование паролей
│   │   └── dependencies.py         # Общие зависимости (auth, DB session)
│   ├── crud/
│   │   ├── product.py              # CRUD операции для товаров
│   │   ├── order.py                # CRUD операции для заказов
│   │   ├── user.py                 # CRUD операции для пользователей
│   │   └── review.py               # CRUD операции для отзывов
│   ├── models/
│   │   ├── base.py                 # Базовый класс модели
│   │   ├── category.py             # Модель Category
│   │   ├── product.py              # Модель Product
│   │   ├── user.py                 # Модель User
│   │   ├── order.py                # Модель Order
│   │   └── review.py               # Модель Review
│   ├── schemas/
│   │   ├── product.py              # Pydantic схемы для товаров
│   │   ├── order.py                # Pydantic схемы для заказов
│   │   ├── user.py                 # Pydantic схемы для пользователей
│   │   └── review.py               # Pydantic схемы для отзывов
│   ├── web/
│   │   └── router.py               # Роутеры для веб-интерфейса
│   ├── static/                     # Статические файлы (CSS, JS, изображения)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── templates/                  # Jinja2 шаблоны
│   │   ├── base.html               # Базовый шаблон
│   │   ├── home.html               # Главная/каталог
│   │   ├── product-detail.html     # Страница товара
│   │   ├── cart.html               # Корзина
│   │   ├── checkout.html           # Оформление заказа
│   │   ├── login.html              # Вход
│   │   ├── register.html           # Регистрация
│   │   ├── account.html            # Личный кабинет
│   │   └── admin/                  # Админ-панель
│   │       ├── dashboard.html
│   │       └── products.html
│   └── utils/
│       ├── email.py                # Отправка email
│       └── cart.py                 # Утилиты для работы с корзиной
├── alembic/                        # Миграции БД
├── tests/                          # Тесты
│   ├── test_api/
│   ├── test_web/
│   └── test_crud/
├── docker-compose.yml              # Инфраструктура
├── Dockerfile                      # Контейнер приложения
├── main.py                         # Точка входа FastAPI
├── pyproject.toml                  # Зависимости (uv/poetry)
└── README.md
```

> Структура примерная; приоритет — разделение ответственности, читабельность, расширяемость.

---

## 6. Качество кода и инфраструктура

1. **Типизация и докстринги**
    - Аннотации типов в функциях/методах (Python 3.10+).
    - Pydantic схемы для валидации.
    - Докстринги для публичных API/важных модулей.

2. **Линтеры и статическая проверка**
    - `ruff` или `flake8` для стиля кода.
    - `mypy` для типизации.

3. **Тестирование**
    - `pytest` с `pytest-asyncio` для асинхронных тестов.
    - `httpx` для тестирования FastAPI endpoints.
    - Основные сценарии: каталог, корзина, заказ, регистрация/вход, REST API, бизнес-правила.
    - Проверка ограничений (например, нельзя заказать больше, чем в наличии).

4. **Инфраструктура**
    - PostgreSQL.
    - Docker Compose для запуска (приложение и БД и т.д.).
    - Все зависимости задокументированы (`pyproject.toml` или `requirements.txt`).
    - (Бонус) использование `poetry` / `uv` альтернатив.

5. **Git workflow**
    - Осмысленные мелкие коммиты.
    - Ветки: `feature/...`, `develop/...`, стабильный `main`.

6. **Документация**
    - README: описание, установка, запуск, JWT, API-примеры, тесты, линтеры, структура.

---

## 7. API-документация и взаимодействие

- Swagger/OpenAPI для REST API (автоматически на `/docs/`).
- ReDoc альтернатива (автоматически на `/redoc/`).
- Примеры запросов с JWT, объяснение схемы авторизации.
- Формат access/refresh токенов, обновление.
- (Если есть) описание типов и примеры в GraphQL.

---

## 8. Оценивание (грейдинг)

**Максимум — 100 баллов.** Бонусные улучшения не поднимают итог выше 100.

| Критерий                                                       | Баллы |
|----------------------------------------------------------------|-------|
| Каталог и поиск товаров                                        | 10    |
| Детальная страница товара и отзывы                             | 10    |
| Корзина и её обработка                                         | 10    |
| Оформление заказа и email                                      | 10    |
| Личный кабинет и история заказов                               | 10    |
| Админка и аналитика                                            | 10    |
| REST API и документация                                        | 10    |
| Качество кода и инструменты (типизация, линтеры, тесты)        | 10    |
| Инфраструктура (PostgreSQL, Docker, зависимости, git workflow) | 10    |
| README и проектная гигиена (чек-лист, коммиты, структура)      | 5     |
| Бонусы                                                         | 5     |

**Итого:** 100

**Рекомендованные улучшения (не увеличивают выше 100):**

- GraphQL аналитика
- Расширенное покрытие тестами (>=80%)
- CI/CD (проверка тестов и линтеров, сборка, деплои)
- Использование `poetry` или `uv` менеджера
- Кэширование (Redis)
- WebSocket для уведомлений

---

## 9. Требования к сдаче

1. Репозиторий на GitHub с кодом.
2. README.md:
    - Описание
    - Установка и запуск (через Docker)
    - JWT и API-примеры
    - Запуск тестов и линтеров
    - Структура проекта
3. (Опционально) ссылка на деплой / screencast.
4. ФИО и группа + ссылка преподавателю.
5. Чек-лист реализации (отмеченное что сделано).
6. История коммитов / веток.

---

## 10. Чек-лист перед сдачей

- [ ] Проект запускается через Docker Compose на чистой копии.
- [ ] PostgreSQL используется.
- [ ] Каталог: фильтры, поиск, пагинация.
- [ ] Страница товара: детали, отзывы, добавление в корзину.
- [ ] Корзина: управление, расчёт, проверка остатков.
- [ ] Оформление заказа: создание, email, валидация.
- [ ] Личный кабинет: регистрация, вход, история, редактирование.
- [ ] REST API: JWT, документация, права.
- [ ] Админка: аналитика, фильтры, управление.
- [ ] Swagger/OpenAPI работает (`/docs/`).
- [ ] Типизация и докстринги.
- [ ] Линтеры (ruff/mypy) без критичных ошибок.
- [ ] Базовые тесты проходят.
- [ ] README полон и понятен.
- [ ] Коммиты осмысленные, ветки используются.
- [ ] Чек-лист приложен.

---

## 11. Роадмап и таймлайн (рекомендовано)

**Рекомендуемый срок:** 3 недели

### Неделя 1

1. Инициализация: Docker, PostgreSQL, шаблоны, статика.
2. Модели: Category, Product, User, Order, OrderItem, Review (SQLAlchemy).
3. Миграции: Alembic, создание таблиц.
4. Каталог: список, фильтры, поиск, пагинация (веб-интерфейс).

### Неделя 2

5. Страница товара: отзывы, корзина.
6. Корзина: сессии, управление.
7. Оформление заказа: форма, email.
8. Личный кабинет: регистрация, история, редактирование.

### Неделя 3

9. Админка: кастомизация, статистика.
10. REST API: роутеры, JWT, документация.
11. Качество: линтеры, типизация, тесты, README.
12. (Бонус) GraphQL / CI / расширенные тесты.
13. Финальная проверка.

---

## 12. Технические детали FastAPI

### 12.1. Аутентификация и авторизация

**Веб-интерфейс (Session-based):**
```python
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Depends, Request

# В main.py
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Зависимость для проверки авторизации
async def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id
```

**REST API (JWT):**
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
```

### 12.2. Работа с базой данных

**Асинхронная сессия:**
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

**Использование в роутерах:**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/products/")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products
```

### 12.3. Работа с формами

```python
from fastapi import Form

@router.post("/login/")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Обработка формы
    pass
```

### 12.4. Статические файлы и шаблоны

```python
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
```

### 12.5. Пагинация

```python
from fastapi import Query

@router.get("/products/")
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product).offset(skip).limit(limit)
    )
    products = result.scalars().all()
    return products
```

---

## 13. Отличия от Django версии

1. **Асинхронность:** FastAPI использует async/await по умолчанию для работы с БД.
2. **ORM:** SQLAlchemy вместо Django ORM (более явный контроль над запросами).
3. **Шаблоны:** Jinja2 напрямую, без Django template tags (но синтаксис похож).
4. **Сессии:** Использование Starlette SessionMiddleware вместо Django sessions.
5. **Формы:** FastAPI Form вместо Django Forms (более простой подход).
6. **Админка:** Нет встроенной админки, нужно создавать кастомную или использовать библиотеки.
7. **Миграции:** Alembic вместо Django migrations.
8. **Документация API:** Автоматическая через OpenAPI (встроена в FastAPI).

---

## 14. Полезные библиотеки

- `fastapi` - основной фреймворк
- `sqlalchemy[asyncio]` - асинхронный ORM
- `alembic` - миграции
- `python-jose[cryptography]` - JWT
- `passlib[bcrypt]` - хеширование паролей
- `python-multipart` - для работы с формами
- `jinja2` - шаблоны
- `aiosmtplib` или `fastapi-mail` - отправка email
- `pytest` + `pytest-asyncio` + `httpx` - тестирование
- `ruff` или `flake8` - линтер
- `mypy` - проверка типов

---

## 15. Заключение

Это ТЗ адаптировано для FastAPI с учётом особенностей фреймворка: асинхронность, SQLAlchemy, встроенная документация API, и более гибкая архитектура. Основные принципы и функциональные требования остаются теми же, что и в Django версии, но реализация будет отличаться в соответствии с философией FastAPI.
