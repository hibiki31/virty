from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mixin.settings import virty_root

DATABASE_PATH = virty_root + "/data/app.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///" + DATABASE_PATH


Engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)


# プリントでデバッグしやすいように
class RepresentableBase(object):
    def __repr__(self):
        columns = ', '.join([
            '{0}={1}'.format(k, repr(self.__dict__[k]))
            for k in self.__dict__.keys() if k[0] != '_'
        ])
        return '<{0}({1})>'.format(
            self.__class__.__name__, columns
        )


# 全てのクラスに共通のスーパークラスを追加
Base = declarative_base(cls=RepresentableBase)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()