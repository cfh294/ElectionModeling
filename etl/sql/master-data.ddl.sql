create view master_data as
with year_to_census as (
	select '2020' year, '2010' census union
	select '2018' year, '2010' census union
	select '2016' year, '2010' census union
	select '2014' year, '2010' census union
	select '2012' year, '2010' census union
	select '2010' year, '2000' census union
	select '2008' year, '2000' census union
	select '2006' year, '2000' census union
	select '2004' year, '2000' census union
	select '2002' year, '2000' census union
	select '2000' year, '1990' census
)
select   cw.party
       , cw.year
	, cast(cw.county_fips as integer) county_fips
       , cw.votes
       , case when cw.votes is 0 then 0 else cw.pct end vote_pct
       , cp.population county_population
       , sp.population state_population
       , chi.uninsured
       , chi.uninsured_pct
       , cast(cps.people_in_poverty as integer) people_in_poverty
       , cast(cps.poverty_rate as float) poverty_rate
       , cg.area_land county_area_land
       , cg.area_water county_area_water
       , 100 * (cg.area_land / (cg.area_land + cg.area_water)) county_pct_land
       , 100 * (cg.area_water / (cg.area_land + cg.area_water)) county_pct_water
       , sg.area_land state_area_land
       , sg.area_water state_area_water 
       , 100 * (sg.area_land / (sg.area_land + sg.area_water)) state_pct_land
       , 100 * (sg.area_water / (sg.area_land + sg.area_water)) state_pct_water
from county_winners cw
left join year_to_census yc on cw.year = yc.year
left join county_population cp on cw.county_fips = cp.county_id and yc.census = cp.census_year
left join state_population sp on cw.state_fips = sp.state_id and yc.census = sp.census_year 
left join county_health_insurance_statistic chi on cw.county_fips = chi.county_id and cw.year = chi.year
left join county_geography cg on cw.county_fips = cg.county_id
left join state_geography sg on cw.state_fips = sg.state_id
left join county_poverty_statistic cps on yc.census = cps.year and cw.county_fips = cps.county_id
where cw.county_fips is not null
;