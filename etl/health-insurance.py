#!/usr/bin/env python3
"""
Load health insurance info into SQLITE
Source csv compiled from:
https://www.census.gov/data-tools/demo/sahie/#/?map_yearSelector=2011&s_year=2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018
"""
import csv
import pathlib
from utils import database_string, get_session
from models import CountyHealthInsuranceStatistic, County

_path = str(pathlib.PurePath(".", "base-data", "health-insurance.csv"))
_fields = ["year", "fips", "pop", "uninsured", "uninsured_pct", "insured", "insured_pct"]

def main():
    session = get_session(database_string)

    with open(_path, "r") as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=_fields)
        next(reader)

        fips_to_county = {}
        state_fips = set()
        for row in reader:
            fips = str(row.get("fips")).zfill(6)
            if fips in state_fips:
                county = None
            else:
                if fips in fips_to_county:
                    county = fips_to_county[fips]
                else:
                    county = session.query(County).filter_by(id=fips).first()
                    if county:
                        fips_to_county[fips] = county
                    else:
                        county = None
                        state_fips.add(fips)

            if county:
                insured = row.get("insured")
                uninsured = row.get("uninsured")
                insured_pct = row.get("insured_pct")
                uninsured_pct = row.get("uninsured_pct")
                if insured:
                    if insured == "N/A":
                        insured = None
                        insured_pct = None
                    else:
                        insured = int(insured.replace(",", ""))
                if uninsured:
                    if uninsured == "N/A":
                        uninsured = None
                        uninsured_pct = None
                    else:
                        uninsured = int(uninsured.replace(",", ""))
                
                session.merge(
                    CountyHealthInsuranceStatistic(
                        county_id=county.id,
                        year=row.get("year"),
                        insured=insured,
                        insured_pct=insured_pct,
                        uninsured=uninsured,
                        uninsured_pct=uninsured_pct
                    )
                )
    session.commit()
    session.close()

if __name__ == "__main__":
    main()