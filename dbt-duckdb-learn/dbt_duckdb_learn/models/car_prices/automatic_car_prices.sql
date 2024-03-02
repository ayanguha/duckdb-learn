

select *
from {{ source('source_car_prices', 'car_prices') }}
where transmission = 'automatic'
