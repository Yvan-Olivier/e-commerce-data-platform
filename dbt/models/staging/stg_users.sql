{{
  config(
    materialized='view',
    description='Cleaned user data from raw Users table'
  )
}}

SELECT 
    id as user_id,
    username,
    email,
    phone
FROM {{ source('raw', 'Users') }}