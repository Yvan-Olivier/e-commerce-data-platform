{{
  config(
    materialized='table',
    description='User dimension table for analytics'
  )
}}

SELECT 
    user_id,
    username,
    email,
    phone
FROM {{ ref('stg_users') }}