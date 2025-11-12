# digitalpathai
This is the web container

# Project Structure

django_app/
│── src/  (Django project)
│   ├── core/
│   │   ├── celery.py
│   │   ├── settings.py
│   │   ├── wsgi.py
│   ├── helpers/
│   │   ├── cloudflare/
│   │   │   ├── settings.py
│   │   │   ├── storages.py
│   │   ├── storages/
│   │       ├── mixis.py
│   ├── locale/
│   │   ├── en/
|   │   │   ├── LC_MESSAGES/
|   │   │   │   ├── django.mo
|   │   │   │   ├── django.po
│   │   ├── de/
|   │   │   ├── LC_MESSAGES/
|   │   │   │   ├── django.mo
|   │   │   │   ├── django.po
│   ├── dashboard/
│   ├── static/  (Stored in R2)
│   ├── media/   (Stored in R2)
│   ├── templates/
│   ├── docker-entrypoint.sh
│   ├── manage.py
│   ├── requirements.txt
│── nginx/
│   ├── nginx.conf  (Nginx configuration)
│── .env  (Environment variables)
│── Dockerfile  (Django Docker setup)
│── docker-compose.yml  (Orchestrating containers)



# Project Structure

django_app/
│── src/  (Django project)
│   ├── core/
│   │   ├── celery.py
│   │   ├── settings.py
│   │   ├── wsgi.py
│   ├── static/  (Stored in R2)
│   ├── media/   (Stored in R2)
│   ├── templates/
│   ├── docker-entrypoint.sh
│   ├── manage.py
│   ├── requirements.txt
│── nginx/
│   ├── nginx.conf  (Nginx configuration)
│── .env  (Environment variables)
│── Dockerfile  (Django Docker setup)
│── docker-compose.yml  (Orchestrating containers)

