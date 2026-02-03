{{
  config(
    materialized='view',
    description='Cleaned product data from raw Products table'
  )
}}

SELECT 
    id as product_id,
    title as product_name,
    ROUND(price, 2) as product_price,
    category as product_category,
    description as product_description
FROM {{ source('raw', 'Products') }}