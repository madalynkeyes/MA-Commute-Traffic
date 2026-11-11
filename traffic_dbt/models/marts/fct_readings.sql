{{ config(
    partition_by={'field': 'collected_date_mt', 'data_type': 'date'},
    cluster_by=['segment_id']
) }}

WITH readings AS (
    SELECT * FROM {{ ref('stg_readings') }}
),

deduped AS (
    SELECT *
    FROM readings
    QUALIFY ROW_NUMBER() OVER (PARTITION BY segment_id, collected_at)=1
),

segments AS (
    SELECT * FROM {{ ref('segments') }}
)

SELECT
    deduped.*,segments.road, segments.direction, segments.seq, 
    DATETIME(TIMESTAMP_SECONDS(900 * DIV(UNIX_SECONDS(collected_at), 900)), 'America/Denver') AS poll_slot_mt,
    DATE(collected_at_mt) AS collected_date_mt,
    EXTRACT(HOUR FROM collected_at_mt) AS hour_mt,
    FORMAT_DATETIME('%A',collected_at_mt) AS day_of_week,
    SAFE_DIVIDE(current_speed_mph, free_flow_speed_mph) AS congestion_ratio
FROM deduped
LEFT JOIN segments ON deduped.segment_id = segments.segment_id
