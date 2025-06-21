from auth.function import get_password_hash, verify_password


def test_bcrypt(clean_user_table):
    pw = "virty-pytest-bcrypt"
    pw_hash = get_password_hash(pw)
    
    assert verify_password(plain_password=pw, hashed_password=pw_hash)
    
    