create view state_geography as
with base as (
	select substr(county_id,1,3) state_id 
	     , area_water
	     , area_land
	from county_geography 
)
select substr(state_id || '000000', 1, 6)
     , sum(area_water) area_water
     , sum(area_land)  area_land
from base
group by state_id
;