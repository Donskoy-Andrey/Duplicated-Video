FROM python:3.11

WORKDIR /app

ENV PYTHONPATH=/app

RUN mkdir -p /duplicates/backend

COPY ./duplicates/backend/__init__.py /app/duplicates/__init__.py

COPY ./pyproject.toml ./

COPY ./poetry.lock ./

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN python -m pip install --upgrade pip

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install

RUN poetry add git+https://github.com/facebookresearch/pytorchvideo.git
