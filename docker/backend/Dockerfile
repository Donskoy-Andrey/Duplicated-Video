FROM python:3.11

WORKDIR /app

COPY ./pyproject.toml ./

#COPY ./poetry.lock ./

RUN python -m pip install --upgrade pip

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install