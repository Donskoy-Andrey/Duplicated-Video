from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BIND_IP: str = '0.0.0.0'
    BIND_PORT: int = 8001
    METRICS_APP_PORT: int = 8081

    BACKEND_CORS_ORIGINS: list[str] = []

    LOG_LEVEL: str = 'DEBUG'

    RABBITMQ_HOST: str = 'localhost'
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USERNAME: str = 'guest'
    RABBITMQ_PASSWORD: str = 'guest'
    RABBITMQ_VIRTUALHOST: str = ''
    RABBITMQ_CONNECTION_POOL_SIZE: int = 2
    RABBITMQ_CHANNEL_POOL_SIZE: int = 10

    EXCHANGE: str = 'your_exchange'
    QUEUE: str = 'your_queue'

    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USERNAME: str = 'postgres'
    DB_PASSWORD: str = 'postgres'
    DB_NAME: str = 'postgres'

    @property
    def db_url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@'
            f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


settings = Settings()
