-- Called by on-run-end: stores one row per model/test result in SIDEFLIX.LAB.DBT_RESULTS.
-- Runtime distinguishes Core/Docker from dbt Projects on Snowflake.
{% macro log_run_results(results) %}
  {% if execute and results | length > 0 %}
    {% set table = target.database ~ '.LAB.DBT_RESULTS' %}
    {% set runtime = 'core' if target.name == 'core' else 'snowflake' %}
    {# LAB already exists from stage4; the runner does not need CREATE SCHEMA. #}
    {% do run_query('create table if not exists ' ~ table ~ ' (
        invocation_id varchar, run_at timestamp_tz, command varchar, runtime varchar,
        node varchar, resource_type varchar, status varchar,
        failures number, execution_seconds number(10,2))') %}
    {% set rows = [] %}
    {% for r in results %}
      {% do rows.append("('" ~ invocation_id ~ "', current_timestamp(), '" ~ flags.WHICH ~ "', '" ~ runtime ~ "', '"
          ~ r.node.unique_id ~ "', '" ~ r.node.resource_type ~ "', '" ~ r.status ~ "', "
          ~ (r.failures if r.failures is not none else 'null') ~ ", " ~ (r.execution_time | round(2)) ~ ")") %}
    {% endfor %}
    {% do run_query('insert into ' ~ table ~ ' values ' ~ rows | join(', ')) %}
  {% endif %}
{% endmacro %}
