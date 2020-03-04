# Set the base image to the base image
FROM hmlandregistry/dev_base_python_flask:5-3.6

# ---- Database stuff start
RUN yum install -y -q postgresql-devel

ENV SQL_HOST=postgres \
 SQL_DATABASE=dpsmetric \
 ALEMBIC_SQL_USERNAME=root \
 SQL_USE_ALEMBIC_USER=no \
 APP_SQL_USERNAME=dpsmetric \
 SQL_PASSWORD=dpsmetric \
 SQLALCHEMY_POOL_RECYCLE="3300"

# ----

# ---- Environment variables

ENV APP_NAME="dps-metric-api" \
 MAX_HEALTH_CASCADE="6" \
 LOG_LEVEL="DEBUG" \
 DEFAULT_TIMEOUT="6"

# ----

# The command to run the app is inherited from lr_base_python_flask

# Get the python environment ready.
# Have this at the end so if the files change, all the other steps don't need to be rerun. Same reason why _test is
# first. This ensures the container always has just what is in the requirements files as it will rerun this in a
# clean image.
ADD requirements_test.txt requirements_test.txt
ADD requirements.txt requirements.txt
RUN pip3 install -q -r requirements.txt && \
  pip3 install -q -r requirements_test.txt
