# Course pack 06 pattern, built from the repository root.
FROM python:3.12.7-slim
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PGHOST=host.docker.internal PGDATABASE=sideflix \
    SNOWFLAKE_DISABLE_PLATFORM_DETECTION=true AWS_EC2_METADATA_DISABLED=true
WORKDIR /app
COPY ingestion/requirements.txt ingestion/requirements.txt
RUN pip install -r ingestion/requirements.txt
COPY ingestion ingestion
COPY source source
RUN useradd --create-home --uid 1000 sideflix && chown -R sideflix /app
USER sideflix
CMD ["python", "ingestion/run_pipeline_job.py", "--help"]
