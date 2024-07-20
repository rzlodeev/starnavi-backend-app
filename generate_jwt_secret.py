# Generate JWT secret key for JWT authentication and store it in .env file

import secrets
from dotenv import load_dotenv, set_key

load_dotenv()

jwt_secret_key = secrets.token_hex(20)

set_key('.env', 'JWT_SECRET_KEY', jwt_secret_key)
