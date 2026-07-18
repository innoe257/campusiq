with source as (
    select * from {{ source('raw', 'predictions') }}
),

renamed as (
    select
        id,
        student_id,
        risk_score,
        risk_category,
        top_factors,
        model_version,
        created_at
    from source
)

select * from renamed
