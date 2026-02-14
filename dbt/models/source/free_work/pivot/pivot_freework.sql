
select
    'dummy' as category,
    count(*) as job_count
from {{ ref('stg_freework') }}
group by 1
