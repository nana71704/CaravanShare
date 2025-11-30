release: python3 -m flask shell -c "from main import db, app; with app.app_context(): db.create_all()"
web: gunicorn --bind 0.0.0.0:$PORT main:app
