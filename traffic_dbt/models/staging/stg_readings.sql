SELECT
  segment_id,
  collected_at,
  DATETIME(collected_at, 'America/Denver') AS collected_at_mt,
  response.currentSpeed AS current_speed_mph,
  response.freeFlowSpeed AS free_flow_speed_mph,
  response.currentTravelTime AS current_travel_time_s,
  response.freeFlowTravelTime AS free_flow_travel_time_s,
  response.confidence AS confidence,
  response.roadClosure AS road_closure,
  response.frc AS frc,
  error,
  error IS NOT NULL AS is_error
FROM {{ source('traffic_raw', 'readings_raw') }}