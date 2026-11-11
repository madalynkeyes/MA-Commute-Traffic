-- Returns any poll that doesn't have exactly one row per segment.
-- The test passes when this query returns zero rows.

SELECT
    collected_at,
    COUNT(*) AS n_segments
FROM {{ ref('fct_readings') }}
GROUP BY collected_at
HAVING COUNT(*) != (SELECT COUNT(*) FROM {{ref('segments')}})
