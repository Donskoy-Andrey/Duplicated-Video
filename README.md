# Duplicated Video Search

---

## Основная информация

Решение осеннего хакатона 2024. Поиск дубликатов видео.

## Техническая информация 

### Системные требования

1. **OS `Linux`** (протестировано на `Ubuntu 22.04.3 LTS`).
2. В зависимости от количества `instances` Моделей на бекенде `Triton` требуется от 20 Gb свободной памяти.
3. Наличие `Docker-Compose`.

## Быстрый старт

### 0. Подготовка среды:
#### Архив с дополнительными файлами: 
```
https://drive.google.com/drive/folders/1p7np_TsrfaDXSYIp7a-eJwMKar-ZMiKM?usp=drive_link
```

Из архива необходимо переместить модель `model.pt` по пути `./duplicates/triton/models/video-embedder/1/model.pt`. 
Это необходимо для корректной инициализациии `Triton`-сервера.

### 1. Сборка проекта через Docker-Compose:
```bash
docker compose up --build
```

Собираются основные контейнеры: \
бекенд, фронтенд, тритон-сервер, веб-сервер и прочее.  

Это занимает некоторое время, т.к. общая память, 
задействованная под контейнеры, около 15Gb.

### 2. Остановка контейнеров:

```bash
docker-compose down
```

### 3. Открытое API 

#### Проверка видео на дублирование

```
http://localhost/api/check-video-duplicate
```

   Пример raw-body запроса:
```json
{
    "link": "https://s3.ritm.media/yappy-db-duplicates/b5f191e6-42e0-43f5-8773-560643de17fb.mp4"
}
```
   Пример результата:
```json
{
    "is_duplicate": true,
    "duplicate_for": "314d2988-eb85-4581-8416-da998e036afe"
}
```

### 4. Прочее

<details>
  <summary>Команды для локальной разработки</summary>

1. Локальная сборка проекта
   ```bash
   make setup
   ```
2. Запуск тестирования
    ```bash
    make tests
    ```
3. Запуск линтера кода
    ```bash
    make lint
    ```
   
4. Справочная информация по всем командам
    ```bash
    make help
    ```
</details>

<details>
  <summary>Структура проекта</summary>

```linux
.
├── duplicates       <--- Основной код
│   ├── backend      <--- Бекенд
│   ├── triton       <--- Triton-Бекенд
│   └── frontend     <--- Фронтенд
├── data             <--- Используемые данные
├── docker           <--- Докер-файлы
├── docs             <--- Документация
├── notebooks        <--- Тестирование гипотез, ноутбуки
└── tests            <--- Тесты
```
</details>