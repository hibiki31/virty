import virty_api as api

api.API_URL = "http://localhost:80"

api.auth_login("user2","abcxyz")
api.auth_test()