from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool
from config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    pool_size=Config.SQLALCHEMY_POOL_SIZE,
    pool_timeout=Config.SQLALCHEMY_POOL_TIMEOUT,
    pool_recycle=Config.SQLALCHEMY_POOL_RECYCLE,
    max_overflow=10
)

db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)
