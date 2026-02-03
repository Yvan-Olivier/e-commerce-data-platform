{{
  config(
    materialized='table',
    description='Product dimension table for analytics'
  )
}}

SELECT 
    product_id,
    product_name,
    product_price,
    product_category,
    product_description
FROM {{ ref('stg_products') }}