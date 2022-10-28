
web: python manage.py collectstatic --no-input; gunicorn MasjidApp.wsgi --timeout 15 --keep-alive 5 --log-file - --log-level debug