-- Fails for any poll whose segment count doesn't match the number of
-- segments that were active on that poll's date.

WITH polls AS (
    SELECT
        collected_at,
        collected_date_mt,
        COUNT(*) AS n_segments
    FROM {{ ref('fct_readings') }}
    GROUP BY collected_at, collected_date_mt
),

expected AS (
    SELECT
        p.collected_at,
        COUNT(s.segment_id) AS n_expected
    FROM polls AS p
    JOIN {{ ref('segments') }} AS s
      ON s.active_from <= p.collected_date_mt
     AND (s.active_to IS NULL OR s.active_to >= p.collected_date_mt)
    GROUP BY p.collected_at
)

SELECT p.collected_at, p.n_segments, e.n_expected
FROM polls AS p
JOIN expected AS e USING (collected_at)
WHERE p.n_segments != e.n_expected