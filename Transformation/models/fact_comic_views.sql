{{ config(materialized='table') }}

WITH base AS (
    SELECT
        comic_id,
        LENGTH(title) * 5 AS cost,  -- Cost = (length of title) * 5
        FLOOR(random() * 10000) AS views,  -- Simulated Views
        FLOOR(random() * 10 + 1) AS review_score  -- Simulated Review Score
    FROM {{ ref('dim_comics') }}
)

SELECT * FROM base

