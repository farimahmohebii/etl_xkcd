{{ config(materialized='table') }}

SELECT 
    comic_id,
    title,
    img_url,
    alt_text,
    date_published
FROM {{ source('xkcd_source', 'xkcd_comics') }}

