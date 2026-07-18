with source as (
    select * from {{ source('raw', 'students') }}
),

renamed as (
    select
        id,
        student_id,
        first_name,
        last_name,
        email,
        enrollment_year,
        program,
        major,
        gpa,
        credits_earned,
        credits_attempted,
        attendance_rate,
        engagement_score,
        financial_aid,
        first_generation,
        is_active,
        created_at,
        updated_at
    from source
)

select * from renamed
