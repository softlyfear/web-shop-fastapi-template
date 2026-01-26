#!/usr/bin/env bash

# ==============================================================================
# Утилита управления проектом (Python + uv)
# Написана с помощью Claude Opus 4.5 (Thinking)
# ==============================================================================
#
# Установка (выполнить один раз вручную):
#   chmod +x dev.sh
#   sudo ln -s "$(pwd)/dev.sh" /usr/local/bin/dev
#
# ==============================================================================

set -euo pipefail

# --- Определение директории проекта ---
get_project_dir() {
    local source="${BASH_SOURCE[0]}"
    while [[ -L "$source" ]]; do
        local dir
        dir=$(cd -P "$(dirname "$source")" && pwd)
        source=$(readlink "$source")
        [[ "$source" != /* ]] && source="$dir/$source"
    done
    cd -P "$(dirname "$source")" && pwd
}

PROJECT_DIR=$(get_project_dir)

# --- Цвета ---
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# --- Логирование ---
log()     { echo -e "${GREEN}==>${NC} $1"; }
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# --- Проверки ---
require_command() {
    if ! command -v "$1" &>/dev/null; then
        error "Команда '$1' не найдена. Установите её и повторите попытку."
        exit 1
    fi
}

ensure_project_dir() {
    cd "$PROJECT_DIR" || {
        error "Не удалось перейти в директорию проекта: $PROJECT_DIR"
        exit 1
    }
    info "Рабочая директория: $PROJECT_DIR"
}

# --- Команды ---
cmd_start() {
    log "Запуск приложения..."
    ensure_project_dir
    require_command uv

    if [[ -d "alembic" || -f "alembic.ini" ]]; then
        log "Применение миграций..."
        uv run python -m alembic upgrade head || warn "Миграции пропущены"
    fi

    uv run python main.py
}

cmd_fmt() {
    log "Форматирование и линтинг (Ruff)..."
    ensure_project_dir
    require_command uvx

    uvx ruff format .
    uvx ruff check --fix .
    log "Готово!"
}

cmd_migrate() {
    log "Создание миграции..."
    ensure_project_dir
    require_command uv

    local msg="${2:-}"
    if [[ -z "$msg" ]]; then
        read -rp "Введите описание миграции: " msg
    fi

    if [[ -z "$msg" ]]; then
        error "Описание миграции не может быть пустым"
        exit 1
    fi

    uv run python -m alembic revision --autogenerate -m "$msg"
    uv run python -m alembic upgrade head
    log "Миграция '$msg' создана и применена"
}

cmd_install() {
    log "Установка зависимостей..."
    ensure_project_dir
    require_command uv

    uv sync
    log "Зависимости установлены"
}

cmd_update() {
    log "Обновление всех зависимостей до последних версий..."
    ensure_project_dir
    require_command uv

    info "Обновление lock-файла..."
    uv lock --upgrade

    info "Синхронизация зависимостей..."
    uv sync

    log "Все зависимости обновлены!"
    info "Проверьте изменения в uv.lock и протестируйте проект"
}

cmd_test() {
    log "Запуск тестов..."
    ensure_project_dir
    require_command uv

    if [[ ! -d "tests" ]]; then
        error "Директория tests/ не найдена"
        info "Создайте её командой: dev init-tests"
        exit 1
    fi

    # Передаём все аргументы в pytest
    uv run pytest "${@:--v --tb=short}"
}

cmd_init_tests() {
    log "Инициализация структуры тестов..."
    ensure_project_dir

    if [[ -d "tests" ]]; then
        warn "Директория tests/ уже существует"
        read -rp "Перезаписать файлы? [y/N]: " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            info "Отменено"
            exit 0
        fi
    fi

    mkdir -p tests

    # tests/__init__.py
    cat > tests/__init__.py << 'EOF'
"""Тесты проекта."""
EOF

    # tests/conftest.py
    cat > tests/conftest.py << 'EOF'
"""Общие фикстуры для тестов."""

import pytest


@pytest.fixture
def sample_data():
    """Пример фикстуры с тестовыми данными."""
    return {
        "id": 1,
        "name": "test",
        "active": True,
    }


@pytest.fixture
def temp_file(tmp_path):
    """Фикстура для временного файла."""
    file = tmp_path / "test.txt"
    file.write_text("test content")
    return file


# --- Фикстуры для FastAPI (раскомментировать при необходимости) ---

# from httpx import AsyncClient, ASGITransport
# from main import app  # или откуда у вас импортируется app
#
# @pytest.fixture
# async def client():
#     """Асинхронный клиент для тестирования API."""
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://test"
#     ) as ac:
#         yield ac


# --- Фикстуры для базы данных (раскомментировать при необходимости) ---

# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
#
# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
#
# @pytest.fixture
# async def db_session():
#     """Тестовая сессия БД."""
#     engine = create_async_engine(TEST_DATABASE_URL, echo=False)
#     async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#     async with async_session() as session:
#         yield session
#     await engine.dispose()
EOF

    # tests/test_example.py
    cat > tests/test_example.py << 'EOF'
"""Примеры тестов."""

import pytest


class TestExample:
    """Примеры базовых тестов."""

    def test_always_passes(self):
        """Этот тест всегда проходит."""
        assert True

    def test_basic_math(self):
        """Проверка базовой арифметики."""
        assert 2 + 2 == 4
        assert 10 - 5 == 5
        assert 3 * 4 == 12

    def test_string_operations(self):
        """Проверка строковых операций."""
        text = "Hello, World!"
        assert text.lower() == "hello, world!"
        assert text.startswith("Hello")
        assert "World" in text

    def test_list_operations(self):
        """Проверка операций со списками."""
        items = [1, 2, 3]
        items.append(4)
        assert len(items) == 4
        assert items[-1] == 4

    def test_with_fixture(self, sample_data):
        """Тест с использованием фикстуры."""
        assert sample_data["id"] == 1
        assert sample_data["name"] == "test"
        assert sample_data["active"] is True


class TestExceptions:
    """Примеры тестов исключений."""

    def test_raises_value_error(self):
        """Проверка выброса исключения."""
        with pytest.raises(ValueError):
            int("not_a_number")

    def test_raises_key_error(self):
        """Проверка KeyError."""
        data = {"a": 1}
        with pytest.raises(KeyError):
            _ = data["b"]


class TestParametrized:
    """Примеры параметризованных тестов."""

    @pytest.mark.parametrize("value,expected", [
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
        (5, 25),
    ])
    def test_square(self, value, expected):
        """Параметризованный тест для квадратов чисел."""
        assert value ** 2 == expected

    @pytest.mark.parametrize("input_str,expected_len", [
        ("", 0),
        ("a", 1),
        ("hello", 5),
        ("привет", 6),
    ])
    def test_string_length(self, input_str, expected_len):
        """Параметризованный тест длины строки."""
        assert len(input_str) == expected_len


# --- Асинхронные тесты (раскомментировать при необходимости) ---

# @pytest.mark.asyncio
# async def test_async_operation():
#     """Пример асинхронного теста."""
#     import asyncio
#     await asyncio.sleep(0.1)
#     assert True

# @pytest.mark.asyncio
# async def test_api_health(client):
#     """Тест health endpoint."""
#     response = await client.get("/health")
#     assert response.status_code == 200
EOF

    # pytest.ini
    cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
asyncio_mode = auto
EOF

    log "Структура тестов создана!"
    echo ""
    info "Созданные файлы:"
    echo "    tests/__init__.py"
    echo "    tests/conftest.py"
    echo "    tests/test_example.py"
    echo "    pytest.ini"
    echo ""
    info "Добавьте pytest в зависимости:"
    echo "    uv add --dev pytest pytest-asyncio"
    echo ""
    info "Запуск тестов:"
    echo "    dev test              # все тесты"
    echo "    dev test -k 'math'    # тесты содержащие 'math'"
    echo "    dev test --cov        # с покрытием (нужен pytest-cov)"
}

cmd_clean() {
    log "Очистка кэша и временных файлов..."
    ensure_project_dir

    local dirs=(
        "__pycache__"
        ".pytest_cache"
        ".ruff_cache"
        ".mypy_cache"
        ".coverage"
        "htmlcov"
        ".tox"
        "dist"
        "build"
    )

    local patterns=(
        "*.pyc"
        "*.pyo"
        "*.egg-info"
        ".DS_Store"
    )

    local count=0

    for dir in "${dirs[@]}"; do
        while IFS= read -r -d '' found; do
            rm -rf "$found"
            info "Удалено: $found"
            ((count++))
        done < <(find . -type d -name "$dir" -print0 2>/dev/null)
    done

    for pattern in "${patterns[@]}"; do
        while IFS= read -r -d '' found; do
            rm -f "$found"
            info "Удалено: $found"
            ((count++))
        done < <(find . -type f -name "$pattern" -print0 2>/dev/null)
    done

    if [[ -f ".coverage" ]]; then
        rm -f ".coverage"
        info "Удалено: .coverage"
        ((count++))
    fi

    if ((count == 0)); then
        info "Нечего удалять — проект уже чист"
    else
        log "Очищено объектов: $count"
    fi
}

cmd_help() {
    cat <<EOF
Утилита управления проектом

Использование: ${0##*/} <команда> [аргументы]

Команды:
    start       Запустить приложение (с миграциями)
    fmt         Форматирование и линтинг кода (Ruff)
    migrate     Создать и применить миграцию Alembic
    install     Установить/синхронизировать зависимости
    update      Обновить все зависимости до последних версий
    test        Запуск тестов (pytest)
    init-tests  Создать структуру тестов
    clean       Удаление кэша и временных файлов
    help        Показать эту справку

Примеры:
    ${0##*/} start
    ${0##*/} fmt
    ${0##*/} migrate "add users table"
    ${0##*/} update
    ${0##*/} test
    ${0##*/} test -k "api"
    ${0##*/} test --cov=src
    ${0##*/} init-tests
    ${0##*/} clean
EOF
}

# --- Точка входа ---
main() {
    case "${1:-}" in
        start)      cmd_start ;;
        fmt)        cmd_fmt ;;
        migrate)    cmd_migrate "$@" ;;
        install)    cmd_install ;;
        update)     cmd_update ;;
        test)       shift; cmd_test "$@" ;;
        init-tests) cmd_init_tests ;;
        clean)      cmd_clean ;;
        help|-h|--help) cmd_help ;;
        "")
            error "Команда не указана"
            echo ""
            cmd_help
            exit 1
            ;;
        *)
            error "Неизвестная команда: $1"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"