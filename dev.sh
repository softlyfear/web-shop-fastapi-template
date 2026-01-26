#!/usr/bin/env bash

# ==============================================================================
# Утилита управления проектом (Python + uv)
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
    # Разрешаем симлинки
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

cmd_help() {
    cat <<EOF
Утилита управления проектом

Использование: ${0##*/} <команда> [аргументы]

Команды:
    start       Запустить приложение (с миграциями)
    fmt         Форматирование и линтинг кода (Ruff)
    migrate     Создать и применить миграцию Alembic
                Пример: ${0##*/} migrate "add users table"
    install     Установить/синхронизировать зависимости (uv sync)
    help        Показать эту справку

Примеры:
    ${0##*/} start
    ${0##*/} fmt
    ${0##*/} migrate "initial"
    ${0##*/} install
EOF
}

# --- Точка входа ---
main() {
    case "${1:-}" in
        start)   cmd_start ;;
        fmt)     cmd_fmt ;;
        migrate) cmd_migrate "$@" ;;
        install) cmd_install ;;
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