# 이 명령어는 PostgreSQL에 접속하여 db.create_all()을 실행합니다.
release: python3 -m flask shell -c "from main import db, app; with app.app_context(): db.create_all()"

# web 명령어: 서버를 시작합니다.
web: gunicorn --bind 0.0.0.0:$PORT main:app
