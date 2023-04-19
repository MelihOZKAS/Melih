#python kurulumu
FROM python:3.10-slim



RUN apt-get update && apt-get install -y python3-dev build-essential libpq-dev postgresql-client


ENV PYTHONDONTWRITEBYTECODE 1
ENV VIRTUAL_ENV=/opt/venv



RUN pip install --upgrade pip
RUN pip install virtualenv && python -m virtualenv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"


ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY entrypoint.sh /srv/entrypoint.sh
RUN sed i 's/\r$//g' /srv/entrypoint.sh
RUN chmod +x /srv/entrypoint.sh

COPY . /srv/app
WORKDIR /srv/app


ENTRYPOINT ["/srv/entrypoint.sh"]