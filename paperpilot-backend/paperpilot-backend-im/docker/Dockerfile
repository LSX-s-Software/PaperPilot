ARG PYTHON_VERSION=3.11-slim-bullseye

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage

ARG DJANGO_ENV=production

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  git

RUN pip install poetry

WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock /tmp/

RUN echo "$DJANGO_ENV" \
    && poetry config virtualenvs.create false \
    && poetry export \
       $(if [ "$DJANGO_ENV" = 'development' ]; then echo '--with dev'; fi) \
       --output requirements.txt --without-urls

# RUN poetry install

RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r requirements.txt

# PaperPilot
RUN pip wheel --wheel-dir /usr/src/app/wheels git+https://github.com/Nagico/paperpilot-common.git#subdirectory=paperpilot-common-python

# Delete setuptools and pip to avoid conflicts with the system packages
RUN rm -rf /usr/src/app/wheels/setuptools* /usr/src/app/wheels/pip*

FROM python as python-run-stage

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  vim \
  curl \
  wget \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# change mirror
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

# Install grpcurl
RUN mkdir grpcurl && cd grpcurl \
  && wget https://github.com/fullstorydev/grpcurl/releases/download/v1.8.8/grpcurl_1.8.8_linux_x86_64.tar.gz \
  && tar -xvf grpcurl_1.8.8_linux_x86_64.tar.gz \
  && mv grpcurl /usr/local/bin \
  && cd .. && rm -rf grpcurl

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/

# copy application code to WORKDIR
COPY  ./run.py run.py
COPY ./server/ server/

EXPOSE 8001

HEALTHCHECK --interval=10s --timeout=5s \
  CMD grpcurl -d '{}' -plaintext -v 127.0.0.1:8001 grpc.health.v1.Health.Check || exit 1

ENTRYPOINT ["python", "run.py", "0.0.0.0:8001"]
