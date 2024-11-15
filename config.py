from fastapi import Depends
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='forbid')
    postgres_url: str
    sheety_bearer: str
    sheety_users_endpoint: str
    coingecko_api_key: str
    coingecko_endpoint: str
    rapidapi_key: str
    rapidapi_endpoint: str
    smtp_username: str
    smtp_password: str
    smtp_hostname: str
    smtp_port: int


settings = Settings()
DATABASE_URL = settings.postgres_url
engine = create_async_engine(DATABASE_URL, echo=False)
Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def async_session():
    async with Session() as session:
        yield session


AsyncSessionDepends = Annotated[AsyncSession, Depends(async_session)]