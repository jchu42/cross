# https://docs.docker.com/language/python/containerize/
#get requirements.txt:
# https://stackoverflow.com/questions/31684375/automatically-create-file-requirements-txt
#gunicorn command not found - add to requirements.txt:
# https://stackoverflow.com/questions/60452279/gunicorn-command-not-found-but-its-in-my-requirements-txt
# https://www.google.com/search?q=get+gunicorn+version&rlz=1C1BFEM_enCA1074CA1074&oq=get+gunicorn+version+&gs_lcrp=EgZjaHJvbWUyCggAEEUYFhgeGDkyCAgBEAAYFhgeMg0IAhAAGIYDGIAEGIoFMg0IAxAAGIYDGIAEGIoFMg0IBBAAGIYDGIAEGIoF0gEIMzkzNmowajeoAgCwAgA&sourceid=chrome&ie=UTF-8
#fixing psycopg2 dependencies
# https://stackoverflow.com/questions/76164877/fail-dockerizing-django-postgresql-project-due-to-problem-with-installing-psyco
#modifying compose.yaml file for the database
# https://www.docker.com/blog/how-to-use-the-postgres-docker-official-image/

FROM python:3.11.5
WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# install system dependencies
RUN apt-get update

RUN apt-get install -y gcc libpq-dev

# install dependencies
RUN pip install --upgrade pip

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app


ENTRYPOINT [ "gunicorn", "project.wsgi:application", "-b", "0.0.0.0:8000"]