create view state_population as
with base as (
	select substr(county_id, 1, 3) state_id
	     , census_year
	     , population
	from county_population
)
select substr(state_id || '000000', 1, 6) state_id
     , census_year
     , sum(population) population
from base 
group by state_id, census_year
;