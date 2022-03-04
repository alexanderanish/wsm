
FROM python:3.9


WORKDIR /usr/src/app

# set environment varibles
# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DB_NAME="farmstack"
ENV DB_URL="mongodb://127.0.0.1:27017"
ENV JWT_SECRET_KEY="b750fab2229674e86d5fddeb9e61af884a3c612560f3d4ae6fd03206d0885309"

COPY ./requirements.txt /usr/src/app/requirements-docker.txt


RUN pip install -r /usr/src/app/requirements-docker.txt --use-deprecated=legacy-resolver
pip install fastapi-mail

COPY . /usr/src/app/


CMD ["uvicorn", "main:app"]
