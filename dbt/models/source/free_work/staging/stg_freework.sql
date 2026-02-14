
with source as (
    select * from {{ ref('raw_freework') }}
)

select
    -- We will refine columns once we see the actual data structure
    *
from source
