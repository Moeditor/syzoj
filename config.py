import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "mysql://syzoj:tCzYHDFyvyG2yyijcQPUTumFcNiTsiXtAvpPdGo$WBg7kFGKKo@127.0.0.1/syzoj?charset=utf8"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "syzoj", "static", "uploads")
JUDGE_TOKEN = "77783949202395150352388871624955475980489287735056"

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
