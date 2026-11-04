FROM python:3.12.7-slim
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 \
    SNOWFLAKE_DISABLE_PLATFORM_DETECTION=true AWS_EC2_METADATA_DISABLED=true \
    DBT_SEND_ANONYMOUS_USAGE_STATS=false DBT_TARGET_PATH=/tmp/dbt-target DBT_LOG_PATH=/tmp/dbt-logs
WORKDIR /app
COPY ingestion/requirements.txt ingestion/requirements.txt
COPY dbt/requirements.txt dbt/requirements.txt
RUN pip install -r dbt/requirements.txt
COPY ingestion ingestion
COPY dbt dbt
RUN useradd --create-home --uid 1000 sideflix && chown -R sideflix /app
USER sideflix
CMD ["dbt", "build", "--project-dir", "dbt/sideflix_dbt", "--profiles-dir", "dbt/profiles-core"]
