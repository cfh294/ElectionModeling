#!/usr/bin/env python3
"""
Load 2020 election data by county into the SQLITE db

source: https://raw.githubusercontent.com/tonmcg/US_County_Level_Election_Results_08-20/master/2020_US_County_Level_Presidential_Results.csv
"""

import requests
import io
import csv
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import get_session, database_string
from models import Election, Candidate, Campaign, CountyVoteResult, ElectionType, PoliticalParty, Campaign

_source = "https://raw.githubusercontent.com/tonmcg/US_County_Level_Election_Results_08-20/master/2020_US_County_Level_Presidential_Results.csv"
_cols = ["state_name", "county_fips", "county_name", "votes_gop", "votes_dem", "total_votes", "diff", "per_gop", "per_dem", "per_point_diff"]
_party_code_mappings = {
    "dem" : "D",
    "gop" : "R",
    "oth" : "OTH"
}

def cmd_line(f):
    def wrap(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Load the 2020 federal election json file to a database.")
        ap.add_argument("-c", "--connection", default=database_string, help="Database connection string.", type=str)
        return f(ap.parse_args(), *args, **kwargs)
    return wrap


def get_campaigns(session):
    et = session.query(ElectionType).filter_by(code="PRESIDENTIAL").first()
    election = session.query(Election).filter_by(election_type=et, year=2020).first()
    dems = session.query(PoliticalParty).filter_by(code="D").first()
    reps = session.query(PoliticalParty).filter_by(code="R").first()
    oths = session.query(PoliticalParty).filter_by(code="OTH").first()
    return {
        "D": session.query(Campaign).filter_by(election=election, political_party=dems).first(),
        "R": session.query(Campaign).filter_by(election=election, political_party=reps).first(),
        "OTH": session.query(Campaign).filter_by(election=election, political_party=oths).first(),
    }


@cmd_line
def main(args):
    session = get_session(args.connection)
    campaigns = get_campaigns(session)

    response = requests.get(_source)
    text = io.StringIO(response.text)
    reader = csv.DictReader(text, fieldnames=_cols)
    next(reader)  # skip header

    for row in reader:
        fips = str(row.get("county_fips")).zfill(6)
        votes_dem = int(row.get("votes_dem"))
        votes_gop = int(row.get("votes_gop"))
        votes_tot = int(row.get("total_votes"))
        votes_oth = votes_tot - (votes_gop + votes_dem)

        mapping = {"D": votes_dem, "R": votes_gop, "OTH": votes_oth}
        for party, votes in mapping.items():
            session.merge(
                CountyVoteResult(
                    county_id=fips,
                    campaign=campaigns[party],
                    votes=votes
                )
            )
        session.commit()
        

if __name__ == "__main__":
    main()