import pytest

from mixin.database import SessionLocal
from models import UserModel


@pytest.fixture(scope="function")
def clean_user_table():
    db = SessionLocal()
    
    db.query(UserModel).delete()
    db.commit()