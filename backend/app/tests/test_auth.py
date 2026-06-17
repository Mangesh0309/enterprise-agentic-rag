from app.auth.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_token_contains_subject():
    token = create_access_token("user-123", {"role": "admin"})

    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"
