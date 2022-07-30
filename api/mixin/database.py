from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import SQLALCHEMY_DATABASE_URL


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
    
    def toDict(self):
        model = {}
        for column in self.__table__.columns:
            model[column.name] = str(getattr(self, column.name))
        return model


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_url():
    return SQLALCHEMY_DATABASE_URL


Engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# 全てのクラスに共通のスーパークラスを追加
Base = declarative_base(cls=RepresentableBase)