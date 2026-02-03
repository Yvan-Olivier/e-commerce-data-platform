{{
  config(
    materialized='table',
    description='Order facts table - center of star schema',
    partition_by={
      "field": "order_date",
      "data_type": "date"
    }
  )
}}

SELECT 
    event_id as order_id,
    cart_id,
    user_id,
    cart_timestamp as order_timestamp,
    DATE(cart_timestamp) as order_date,
    total_items
FROM {{ ref('stg_cart_events') }}