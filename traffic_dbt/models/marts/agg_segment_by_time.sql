WITH readings AS (
    SELECT * FROM {{ ref('fct_readings') }}
),

clean AS (
    SELECT *
    FROM readings
    WHERE is_error = FALSE AND confidence >= 0.6 AND hour_mt BETWEEN 6 AND 19
)

SELECT
    segment_id,
    road,
    direction,
    seq,
    day_of_week,
    TIME(poll_slot_mt) AS time_slot,
    COUNT(*) AS n_readings,
    ROUND(AVG(current_speed_mph), 1) AS avg_speed_mph,
    ROUND(AVG(free_flow_speed_mph),1) AS avg_free_flow_mph,
    ROUND(AVG(congestion_ratio), 2) AS avg_congestion_ratio,
    ROUND(AVG(current_travel_time_s - free_flow_travel_time_s),0) AS avg_delay_s
FROM clean
GROUP BY segment_id, road, direction, seq, day_of_week, time_slot