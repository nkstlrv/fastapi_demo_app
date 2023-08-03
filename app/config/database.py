from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite
# engine = create_engine(
#     "sqlite:///./notes.db", connect_args={"check_same_thread": False}
# )

# MySQL
engine = create_engine(
    "mysql+pymysql://root:mysql@localhost/mysql",
    connect_args={"charset": "utf8mb4"},
)

Base = declarative_base()

MySession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = MySession()
    try:
        yield db
    finally:
        db.close()
