-- How many events are there for each kind of event?

SELECT event_name,
       COUNT(*) AS event_count
  FROM cloudtrail
 GROUP BY event_name
;

-- What percentage of events are errors?
SELECT 100.0 * COUNT(CASE WHEN error_code <> 'None' THEN error_code ELSE NULL END) / COUNT(*) AS pct_errors
  FROM cloudtrail
;

-- For each distinct User Identity Acount ID, what is the mean time between events?

WITH events AS (
-- SQLite3 doesn't have native json support so I'll use this substring in a CASE statement to get account_id.
SELECT CASE
           WHEN user_identity LIKE '%accountId%'
           THEN SUBSTR(user_identity,
                       INSTR(user_identity, 'accountId') + 13,
                       INSTR(SUBSTR(user_identity, INSTR(user_identity, 'accountId') + 13, 30), "'") - 1)
           ELSE NULL
       END AS account_id,
       event_time
  FROM cloudtrail
),
last_event AS (
SELECT account_id,
       event_time,
       LAG(event_time) OVER (PARTITION BY account_id ORDER BY event_time) AS time_of_last_event
  FROM events
)

SELECT account_id,
       ROUND(AVG((JULIANDAY(event_time) - JULIANDAY(time_of_last_event)) * 86400)) AS time_lag_seconds
  FROM last_event 
 GROUP BY account_id
;

