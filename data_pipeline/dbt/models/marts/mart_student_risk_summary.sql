with students as (
    select * from {{ ref('stg_students') }}
),

predictions as (
    select * from {{ ref('stg_predictions') }}
),

latest_predictions as (
    select
        student_id,
        risk_score,
        risk_category,
        top_factors,
        row_number() over (partition by student_id order by created_at desc) as rn
    from predictions
),

student_risk as (
    select
        s.*,
        lp.risk_score,
        lp.risk_category
    from students s
    left join latest_predictions lp on s.id = lp.student_id and lp.rn = 1
),

aggregated as (
    select
        program,
        enrollment_year as cohort,
        count(*) as total_students,
        avg(gpa) as avg_gpa,
        avg(risk_score) as avg_risk_score,
        count(case when risk_category = 'critical' then 1 end) as critical_count,
        count(case when risk_category = 'high' then 1 end) as high_count,
        count(case when risk_category = 'medium' then 1 end) as medium_count,
        count(case when risk_category = 'low' then 1 end) as low_count,
        count(case when financial_aid then 1 end) as financial_aid_count,
        count(case when first_generation then 1 end) as first_gen_count
    from student_risk
    group by program, enrollment_year
)

select * from aggregated
