#!/usr/bin/env python3
"""
Load 2000-2016 election by county data into SQLITE db
"""
import csv
import argparse
import pathlib
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from utils import get_session, get_campaign, database_string
from models import CountyVoteResult

_path = str(pathlib.Path(".", "base-data", "2000-2016.csv"))
_party_map = { 
    "democrat" : "D", 
    "republican" : "R", 
    "NA" : "OTH", 
    "green" : "OTH" 
}

def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Loads election data (2000-2016) from csv to sqllite db.")
        ap.add_argument("-c", "--connection", type=str, required=False, default=database_string, help="Database connection string.")
        ap.add_argument("-f", "--file", type=str, required=False, default=_path, help="Path to source data file.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_


def collapse_data(path):
    fields = ["year", "state", "state_po", "county", "fips" ,"office", "candidate", "party", "candidatevotes", "totalvotes", "version"]
    year_fips_party_result = {
        "2000" : dict(), "2004" : dict(), "2008" : dict(), "2012" : dict(), "2016" : dict()
    }
    with open(path, "r") as csv_file:
        dr = csv.DictReader(csv_file, fieldnames=fields)
        next(dr)  # skip header line
        for row in dr:
            fips = str(row.get("fips")).zfill(6)
            year = row.get("year")
            party = _party_map.get(row.get("party"))

            votes = row.get("candidatevotes")
            votes = int(votes) if votes != "NA" else 0

            result_dict = year_fips_party_result[year]

            if fips not in result_dict:
                result_dict[fips] = {}
            result_dict = result_dict[fips]

            if party not in result_dict:
                result_dict[party] = votes
            else:
                result_dict[party] += votes
    return year_fips_party_result


def to_db(session, data):
    year_campaign = {}
    for year in ["2000", "2004", "2008", "2012", "2016"]:
        year_campaign[year] = {}
        for party in ["D", "R", "OTH"]:
            year_campaign[year][party] = get_campaign(session, year, party)

    for year, by_fips in data.items():
        for fips, vote_info in by_fips.items():
            for party, votes in vote_info.items():
                campaign_obj = year_campaign[year][party]
                session.merge(
                    CountyVoteResult(
                        county_id=fips, campaign=campaign_obj, votes=votes
                    )
                )
    session.commit()


@with_args
def main(args):
    session = get_session(args.connection)
    ex = None
    try:
        to_db(
            session, 
            collapse_data(args.file)
        )
    except Exception as e:
        ex = e
        session.rollback()
    finally:
        session.close()
    
    if ex:
        raise ex


if __name__ == "__main__":
    main()