from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate  # 导入 Migrate
from config import Config  # 确保这里正确导入了 Config

import sys
import os

# 获取 python_learning_platform 目录的绝对路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将该目录添加到 sys.path 中
sys.path.insert(0, base_dir)

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# 初始化 Migrate
migrate = Migrate(app, db)  # 添加这一行

from app import models, routes

# 用户加载回调函数
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))