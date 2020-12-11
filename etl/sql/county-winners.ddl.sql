create view county_winners as
select year
     , election_type
     , state_fips
     , state_abbr
     , county_fips
     , county_name
     , party
     , candidate_name 
     , running_mate_name
     , votes
     , pct
from (
	select *
	     , dense_rank() over (partition by year, county_fips order by votes desc) vote_rank
	from county_result_master
) rankings 
where rankings.vote_rank = 1
;
