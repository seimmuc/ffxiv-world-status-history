FROM python:3.10-alpine as fws_app
WORKDIR /fws
# install dependencies from Pipfile.lock
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN apk add --no-cache libpq
RUN apk add --no-cache --virtual build-dependencies gcc musl-dev libpq-dev python3-dev
RUN pipenv install --deploy --system
RUN apk del --no-cache build-dependencies
# copy over the web application
COPY fws_site ./fws_site
COPY ffxivws ./ffxivws

FROM fws_app as fws_web
# install and run server
RUN pip install gunicorn
ENTRYPOINT ["gunicorn", "fws_site.wsgi"]
CMD ["--bind=0.0.0.0:80"]

FROM fws_app as fws_manage
# copy manage.py and run it
COPY manage.py .
ENTRYPOINT ["python", "manage.py"]
CMD ["help"]

FROM nginx:1.23.4-alpine as nginx_rev
# remove existing config
RUN rm /etc/nginx/conf.d/*
# Copy new config
COPY deployment/fws_nginx.conf /etc/nginx/conf.d/fws_nginx.conf
# Copy static files
COPY deployment/static_collected/ /web/static/
COPY ffxivws/static/ /web/static/
