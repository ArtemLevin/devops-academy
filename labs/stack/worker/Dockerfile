FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "celery[redis]==5.5.3"
COPY --chown=65532:65532 tasks.py submit.py ./
USER 65532:65532
