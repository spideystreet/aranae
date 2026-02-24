with freework as (
    select * from {{ ref('int_freework__jobs') }}
),

wttj as (
    select * from {{ ref('int_wttj__jobs') }}
),

unioned as (
    select * from freework
    union all
    select * from wttj
)

select * from unioned
order by publication_date desc
