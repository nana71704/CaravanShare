# db_setup.py (프로젝트 루트에 생성)
import os
from main import app, db

# Flask 애플리케이션 컨텍스트 내에서 db.create_all() 실행
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
