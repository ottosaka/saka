import os

# 项目根目录
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 密钥，用于会话管理
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    # 数据库连接配置
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123456@localhost/python_learning_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False