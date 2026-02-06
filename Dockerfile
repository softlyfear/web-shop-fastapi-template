FROM python:slim

RUN pip install --no-cache-dir uv

WORKDIR /web-shop

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
