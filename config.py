from environs import Env
from dataclasses import dataclass
from typing import Optional
from sqlalchemy import URL

@dataclass
class DB:
    user: str
    password: str
    database: str
    host: str
    port: Optional[int]
    
    url: URL

@dataclass
class DBurl():
    url: URL

@dataclass
class Redis:
    password: Optional[str]
    port: Optional[int]
    host: Optional[str]
    use_redis: Optional[str]

    def data_souce_name(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/0"
        else:
            return f"redis://{self.host}:{self.port}/0"


@dataclass
class TgBot:
    token: str
    admins: list[int]


@dataclass
class Config:
    tgbot: TgBot
    db: DB
    redis: Optional[Redis]
    email: Optional[str] = None
    password: Optional[str] = None


def load_config() -> Config:
    env = Env()
    env.read_env()
    user, password, database, host, port = [env.str(data) for data
                                            in ["DB_USER", "DB_PASSWORD", "DB_DATABASE", "DB_HOST", "DB_PORT"]]
    return Config(
        tgbot=TgBot(
            token=env.str("TOKEN"),
            admins=env.list("ADMINS"),
        ),
        db=DB(
                user=user,
                password=password,
                database=database,
                host=host,
                port=port,
                
                url=URL.create(
                f"postgresql+asyncpg",
                username=user,
                host=host,
                port=port,
                password=password,
                database=database
            ).render_as_string(hide_password=False)
        ),
        redis=Redis(
            use_redis=env.str("USE_REDIS"),
            password=env.str("REDIS_PASS"),
            host=env.str("REDIS_HOST"),
            port=env.str("REDIS_PORT")
        ),
        email=env.str("EMAIL"),
        password=env.str("PASSWORD")
    )


config = load_config()
