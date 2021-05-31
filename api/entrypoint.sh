#!/bin/sh

echo "Starting Docker entry point for Mac";

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py db init
python manage.py db migrate
python manage.py db upgrade
flask db upgrade

# gunicorn --bind 0.0.0.0:5000 --workers 5 --thread 2 run:app
gunicorn --bind 0.0.0.0:5000 run:app

exec "$@"
