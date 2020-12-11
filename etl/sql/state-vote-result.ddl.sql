create view state_vote_result as
with base as (
	select 
	  substr(county_id,1,3) state_id
	, campaign_id
	, votes
	from county_vote_result
	where county_id <> '0000NA'
)
select state_id
     , campaign_id
     , sum(votes) votes
from base 
group by state_id, campaign_id
;