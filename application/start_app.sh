if [ "$1" = "webapp" ]; then
  python manage.py makemigrations
  python manage.py migrate
  
  docker pull nacyot/objectivec-gcc:apt
  docker pull perl:5.20
  docker pull ruby:2.1
  docker pull williamyeh/scala

  docker build -t lisp /src/pro1oh1/docker_images/lisp/.

  python manage.py runserver 0.0.0.0:8000
elif [ "$1" = "worker" ]; then
  docker pull bash:4.4
  docker pull java:7
  docker pull gcc:4.9
  docker pull python:2
  docker pull golang:1.6

  celery -A pro1oh1 worker -l info
fi
