# import os - used to construct the path to the .env file
# base settings - used to define the Settings class that will read environment variables from the .env file
import os
from pydantic_settings import BaseSettings

# construct the path to the .env file, which is located in the same directory as this config.py file 
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

# define the Settings class that will read environment variables from the .env file
class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/monika_cafe_db"
    JWT_SECRET: str = "super_secret_jwt_key_monika_cafe"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""

# define the Config class that will specify the path to the .env file and ignore any extra environment variables
    class Config:
        env_file = env_path
        extra = "ignore"
        
# create an instance of the Settings class, which will read the environment variables from the .env file
settings = Settings()

