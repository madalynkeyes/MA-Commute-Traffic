-- One row per segment: the road shape TomTom measured, as a line.
SELECT
    segment_id,
    ST_MAKELINE(ARRAY(
        SELECT ST_GEOGPOINT(c.longitude, c.latitude)
        FROM UNNEST(response.coordinates.coordinate) AS c WITH OFFSET AS i
        ORDER BY i
    )) AS segment_line
FROM {{ source('traffic_raw', 'readings_raw') }}
WHERE response IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY segment_id ORDER BY collected_at DESC) = 1