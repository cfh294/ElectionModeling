create view campaign_descriptive as
select 
    el.year
  , et.description election_type
  , p.name political_party
  , main_cand.display_name candidate
  , vp_cand.display_name running_mate
from campaign base
left join candidate main_cand on base.candidate_id=main_cand.id
left join candidate vp_cand   on base.running_mate_id=vp_cand.id
left join election  el        on base.election_id=el.id
left join election_type et    on el.election_type_id=et.id
left join political_party p   on base.political_party_id=p.id
;