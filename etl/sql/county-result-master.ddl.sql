create view county_result_master as
with totals as (
    select c.year election_year
         , d.id election_type
         , a.county_id
         , sum(a.votes) county_total
    from county_vote_result a
    left join campaign b on a.campaign_id=b.id
    left join election c on b.election_id=c.id
    left join election_type d on c.election_type_id=d.id
    group by c.year, d.id, a.county_id
)
select election.year
     , election_type.code election_type
     , state.id state_fips
     , state.code state_abbr
     , county.id county_fips
     , county.name county_name
     , pp.code party
     , candidate.display_name candidate_name
     , vp.display_name running_mate_name
     , cvr.votes
     , 100 * (cast(cvr.votes as float) / cast(totals.county_total as float)) pct
from county_vote_result cvr 
left join county on cvr.county_id=county.id
left join state on county.state_id=state.id
left join campaign on cvr.campaign_id=campaign.id
left join candidate on campaign.candidate_id=candidate.id
left join candidate vp on campaign.running_mate_id=vp.id
left join political_party pp on campaign.political_party_id=pp.id
left join election on campaign.election_id=election.id
left join election_type on election.election_type_id=election_type.id
left join totals on totals.county_id=cvr.county_id and totals.election_year=election.year and totals.election_type=election_type.id
;