{{
  config(
    materialized='view',
    description='Cleaned cart events from streaming pipeline'
  )
}}

SELECT 
    event_id,
    cart_id,
    user_id,
    TIMESTAMP(cart_date) as cart_timestamp,
    total_items
FROM {{ source('raw', 'carts_events') }}