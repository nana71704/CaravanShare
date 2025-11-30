# db_setup.py 파일 생성 및 내용
from main import app, db

# Flask 애플리케이션 컨텍스트 내에서 db.create_all() 실행
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
