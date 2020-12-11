#!/usr/bin/env python3
"""
Absolutely disgusting, quick, and dirty python script to initialize a bunch of 
key values in the database
"""
import argparse
import datetime
import pathlib
import csv
import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import ModelWhereClause, ModelDropCol, ModelCode, Campaign, PoliticalParty, State, County, ElectionType, Election, Candidate

base_data = pathlib.Path(".", "base-data")

def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Provide a connection string to create all needed DB objects.")
        ap.add_argument("-db", "--database", default="sqlite:///election.db", type=str, help="Database connection string.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_


@with_args
def main(args):
    engine = create_engine(args.database)
    session = sessionmaker(bind=engine)()

    session.merge(ModelCode(id="HI", description="Health insurance and voting"))
    session.merge(ModelCode(id="VO", description="Voting Only"))
    session.merge(ModelCode(id="PV", description="Poverty and voting"))
    session.merge(ModelCode(id="IN", description="Income and voting"))
    session.merge(ModelCode(id="PP", description="Population and voting"))
    session.merge(ModelCode(id="GO", description="Geography and voting"))
    session.merge(ModelCode(id="GP", description="Geography, population, and voting"))
    session.merge(ModelCode(id="IH", description="Health insurance, income, and voting"))
    session.merge(ModelCode(id="ALL", description="All variables"))

    session.merge(ModelCode(id="HI2020", description="Health insurance and voting, including 2020"))
    session.merge(ModelCode(id="VO2020", description="Voting Only, including 2020"))
    session.merge(ModelCode(id="PV2020", description="Poverty and voting, including 2020"))
    session.merge(ModelCode(id="IN2020", description="Income and voting, including 2020"))
    session.merge(ModelCode(id="PP2020", description="Population and voting, including 2020"))
    session.merge(ModelCode(id="GO2020", description="Geography and voting, including 2020"))
    session.merge(ModelCode(id="GP2020", description="Geography, population, and voting, including 2020"))
    session.merge(ModelCode(id="IH2020", description="Health insurance, income, and voting, including 2020"))
    session.merge(ModelCode(id="ALL2020", description="All variables, including 2020"))
    
    mc_mapping = {
        "HI": ["state_population", "county_population", "people_in_poverty", "poverty_rate", "county_area_land", "county_area_water", "county_pct_land", "county_pct_water", "state_area_land", "state_area_water", "state_pct_land", "state_pct_water"],
        "VO": ["uninsured", "uninsured_pct", "state_population", "county_population", "people_in_poverty", "poverty_rate", "county_area_land", "county_area_water", "county_pct_land", "county_pct_water", "state_area_land", "state_area_water", "state_pct_land", "state_pct_water"],
        "PV": ["uninsured", "uninsured_pct", "state_population", "county_population", "county_area_land", "county_area_water", "county_pct_land", "county_pct_water", "state_area_land", "state_area_water", "state_pct_land", "state_pct_water"],
        "PP": ["uninsured", "uninsured_pct", "people_in_poverty", "poverty_rate", "county_area_land", "county_area_water", "county_pct_land", "county_pct_water", "state_area_land", "state_area_water", "state_pct_land", "state_pct_water"],
        "GO": ["uninsured", "uninsured_pct", "state_population", "county_population", "people_in_poverty", "poverty_rate"],
        "GP": ["uninsured", "uninsured_pct", "people_in_poverty", "poverty_rate"],
        "HI2020": ["state_population", "county_population", "people_in_poverty", "poverty_rate", "county_area_land", "county_area_water", "county_pct_land", "county_pct_water", "state_area_land", "state_area_water", "state_pct_land", "state_pct_water"],
        "VO2020": ["uninsured", "uninsured_pct", "state_population", "county_population", "people_in_poverty", "poverty_rate", "county_area_land", "county_area_water", "county_pct_land", "county_pct_water", "state_area_land", "state_area_water", "state_pct_land", "state_pct_water"],
        "PV2020": ["uninsured", "uninsured_pct", "state_population", "county_population", "county_area_land", "county_area_water", "county_pct_land", "county_pct_water", "state_area_land", "state_area_water", "state_pct_land", "state_pct_water"],
        "PP2020": ["uninsured", "uninsured_pct", "people_in_poverty", "poverty_rate", "county_area_land", "county_area_water", "county_pct_land", "county_pct_water", "state_area_land", "state_area_water", "state_pct_land", "state_pct_water"],
        "GO2020": ["uninsured", "uninsured_pct", "state_population", "county_population", "people_in_poverty", "poverty_rate"],
        "GP2020": ["uninsured", "uninsured_pct", "people_in_poverty", "poverty_rate"],
    }

    wc = {
        "ALL": ["year in ('2008', '2012')", "county_population is not null", "state_population is not null", "county_area_land is not null", "county_area_water is not null", "uninsured is not null", "uninsured_pct is not null"],
        "HI": ["year >= '2006'", "year < '2016'", "uninsured is not null", "uninsured_pct is not null"],
        "PV": ["year < 2020", "poverty_rate is not null", "people_in_poverty is not null"],
        "GO": ["year < 2020", "county_area_land is not null", "county_area_water is not null"],
        "GP": ["year < 2020", "county_area_land is not null", "county_area_water is not null", "county_population is not null", "state_population is not null"],
        "PP": ["year < 2020", "county_population is not null", "state_population is not null"],
        "ALL": ["year in ('2008', '2012')", "county_population is not null", "state_population is not null", "county_area_land is not null", "county_area_water is not null", "uninsured is not null", "uninsured_pct is not null"],
        "HI2020": ["year >= '2006'", "year <= '2016'", "uninsured is not null", "uninsured_pct is not null"],
        "PV2020": ["poverty_rate is not null", "people_in_poverty is not null"],
        "GO2020": ["county_area_land is not null", "county_area_water is not null"],
        "GP2020": ["county_area_land is not null", "county_area_water is not null", "county_population is not null", "state_population is not null"],
        "PP2020": ["county_population is not null", "state_population is not null"],
        "ALL2020": ["year in ('2008', '2012', '2016')", "county_population is not null", "state_population is not null", "county_area_land is not null", "county_area_water is not null", "uninsured is not null", "uninsured_pct is not null"],

    }

    for model_code, cols in mc_mapping.items():
        for col in cols:
            session.merge(ModelDropCol(model_code_id=model_code, column=col)) 
    
    for model_code, wcs in wc.items():
        for wc in wcs:
            session.merge(ModelWhereClause(model_code_id=model_code, sql=wc))

    # states and counties
    states = []
    counties = []
    st_abbr_to_fips = dict()
    with open(str(base_data / "fips.csv"), "r") as csv_file:
        cols = ["fips", "name", "state"]
        reader = csv.DictReader(csv_file, fieldnames=cols)
        next(reader)  # skip header
        county_names = ["COUNTY", "PARISH", "BOROUGH", "CENSUS AREA", "MUNICIPALITY", "CITY"]
        for row in reader:
            fips = str(row.get("fips")).zfill(6)
            name = str(row.get("name")).upper()
            state = str(row.get("state")).upper()

            # state
            if not any([n in name for n in county_names]):

                # DC Special case
                if fips == "011000":
                    states.append(
                        State(id=fips, name=name, code=state)
                    )
                    st_abbr_to_fips[state] = fips

                elif fips == "011001":
                    counties.append(
                        County(id=fips, name=name, state_id=st_abbr_to_fips[state])
                    )
                else:
                    states.append(
                        State(id=fips, name=name, code=state)
                    )
                    st_abbr_to_fips[state] = fips
            # county    
            else:
                counties.append(
                    County(id=fips, name=name, state_id=st_abbr_to_fips[state])
                )

        for state in states:
            session.merge(state)
        for county in counties:
            session.merge(county)

    session.merge(PoliticalParty(code="D", name="Democratic Party", founding_year=1828))
    session.merge(PoliticalParty(code="R", name="Republican Party", founding_year=1854))
    session.merge(PoliticalParty(code="OTH", name="Generic Other Candidate"))
    session.merge(PoliticalParty(code="WI", name="Write In Candidate"))
    session.merge(PoliticalParty(code="W", name="Whig Party", founding_year=1833, defunct_ind=True))
    session.merge(PoliticalParty(code="F", name="Federalist Party", founding_year=1791, defunct_ind=True))
    session.merge(PoliticalParty(code="DR", name="Democratic-Republican Party", founding_year=1792, defunct_ind=True))
    session.merge(PoliticalParty(code="L", name="Libertarian Party", founding_year=1971))
    session.merge(PoliticalParty(code="C", name="Constitution Party", founding_year=1990))
    session.merge(PoliticalParty(code="RF", name="Reform Party", founding_year=1995))
    session.merge(PoliticalParty(code="I", name="Independent"))
    session.merge(PoliticalParty(code="G", name="Green Party", founding_year=2001))
    session.merge(PoliticalParty(code="PSL", name="Party for Socialism and Liberation", founding_year=2004))
    session.merge(PoliticalParty(code="SPU", name="Socialist Party USA", founding_year=1973))
    session.merge(PoliticalParty(code="AM", name="Anti-Masonic Party", founding_year=1828, defunct_ind=True))
    session.merge(PoliticalParty(code="DC", name="States' Rights Democratic Party", founding_year=1948, defunct_ind=True)) 
    session.merge(PoliticalParty(code="CU", name="Constitutional Union Party", founding_year=1860, defunct_ind=True)) 
    session.merge(PoliticalParty(code="KN", name="Know Nothing Party", founding_year=1844, defunct_ind=True))
    session.merge(PoliticalParty(code="FS", name="Free Soil Party", founding_year=1848, defunct_ind=True)) 
    session.merge(PoliticalParty(code="NU", name="Nullifier Party", founding_year=1828, defunct_ind=True)) 
    session.merge(PoliticalParty(code="NR", name="National Republican Party", founding_year=1824, defunct_ind=True))   
    session.merge(PoliticalParty(code="AL", name="Alliance Party", founding_year=2018))  
    session.merge(PoliticalParty(code="ADP", name="American Delta Party", founding_year=2016))  
    session.merge(PoliticalParty(code="JU", name="Justice Party", founding_year=2011))  
    session.merge(PoliticalParty(code="NL", name="Natural Law Party", founding_year=1992, defunct_ind=True)) 
    session.merge(PoliticalParty(code="NA", name="New Alliance Party", founding_year=1979, defunct_ind=True)) 
    session.merge(PoliticalParty(code="PO", name="Populist Party", founding_year=1984, defunct_ind=True))


    for t in ["PRESIDENTIAL", "US SENATE", "US HOUSE", "GOVERNOR", "STATE ASSEMBLY", "STATE SENATE"]:
        session.merge(ElectionType(code=t))
    
    presidential = session.query(ElectionType).filter_by(code="PRESIDENTIAL").first()
    for year in range(1788, 2021, 4):
        session.merge(
            Election(election_type=presidential, year=year)
        )

    with open(str(base_data / "candidates.csv"), "r") as csv_file:
        cols = ["first_name", "middle_initial", "last_name", "home_state", "birth_date", "death_date", "nickname", "display_name"]
        reader = csv.DictReader(csv_file, fieldnames=cols)
        next(reader)
        for r in reader:
            home_state = r.get("home_state")
            bd = r.get("birth_date")
            dd = r.get("death_date")
            if home_state:
                home_state_id = session.query(State.id).filter_by(code=home_state).scalar()
            else:
                home_state_id = None
            if bd:
                bd = datetime.datetime.strptime(bd, "%d-%b-%Y").date()
            else:
                bd = None
            if dd:
                dd = datetime.datetime.strptime(dd, "%d-%b-%Y").date()
            else:
                dd = None
            session.merge(
                Candidate(
                    home_state_id=home_state_id, 
                    first_name=r.get("first_name"),
                    last_name=r.get("last_name"),
                    birth_date=bd,
                    death_date=dd,
                    display_name=r.get("display_name"),
                    nickname=r.get("nickname"),
                    middle_initial=r.get("middle_initial")
                )
            )

    with open(str(base_data / "campaigns.csv"), "r") as csv_file:
        cols = ["p_first", "p_last", "vp_first", "vp_last", "party", "year", "election_type"]
        reader = csv.DictReader(csv_file, fieldnames=cols)
        next(reader)

        for row in reader:
            year = int(row.get("year"))
            et = session.query(ElectionType).filter_by(code=row.get("election_type")).first()
            e = session.query(Election).filter_by(year=year, election_type_id=et.id).first()
            fn = row.get("p_first")
            ln = row.get("p_last")
            vpfn = row.get("vp_first")
            vpln = row.get("vp_last")
            p = session.query(PoliticalParty).filter_by(code=row.get("party")).first()
            # bush special case
            if fn == "George" and ln == "Bush":
                if vpfn == "Richard":
                    mi = "W"
                else:
                    mi = "HW"
                cand = session.query(Candidate).filter_by(
                    first_name=fn,
                    last_name=ln,
                    middle_initial=mi
                ).first()
            else:
                cand = session.query(Candidate).filter_by(
                    first_name=fn,
                    last_name=ln
                ).first()
            if vpfn and vpln:
                vp = session.query(Candidate).filter_by(first_name=vpfn, last_name=vpln).first()
            else:
                vp = None
            session.merge(
                Campaign(
                    candidate_id=cand.id,
                    running_mate_id=vp.id if vp else None,
                    election_id=e.id,
                    political_party_id=p.id
                )
            )


    session.commit()
    session.close()


if __name__ == "__main__":
    main()

