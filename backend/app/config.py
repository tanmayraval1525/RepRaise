from dotenv import load_dotenv
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY','a9339199898f7ca4b6c392a5379f9e00b1f45874a9c686458107b552136cb9be')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY','19553b1c5f65bbee2515770bf8364ba0667538fb652b67ce4fc5e26472c3426e')

