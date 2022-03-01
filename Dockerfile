FROM python:3.10-slim

# Installing default dependencies
RUN python3.10 -m pip install -Uq pip pdm

WORKDIR /var/www/

# Copying source files
COPY pyproject.toml pdm.lock ./

# Installing project dependencies
RUN pdm install --prod -G deploy

COPY . .

ENTRYPOINT pdm run circusd ./circus.ini --log-level debug

EXPOSE 8000
