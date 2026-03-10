import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'bb45b05b5d358f69e587e67565b66b83d8f215fee5135135'
    SQLALCHEMY_DATABASE_URI = 'postgresql://babi:root@localhost/hemotrack'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
