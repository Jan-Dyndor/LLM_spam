FROM python:3.14-slim

WORKDIR /app 

RUN mkdir -p /app/data

COPY pyproject.toml .
COPY src ./src

RUN pip install -e . 
RUN pip install "fastapi[standard]"
RUN pip install redis


CMD ["fastapi", "run", "src/app/main.py", "--port", "8000"]