#!/usr/bin/env python3
"""
Load population data into SQLITE
"""
import csv 
import pathlib
import re
from utils import get_session, database_string
from models import CountyPopulation

_path = str(pathlib.PurePath(".", "base-data", "county-population.csv"))
_years = ["1960", "1970", "1980", "1990", "2000", "2010"]
_fields = ["fips"] + _years


if __name__ == "__main__":
    session = get_session(database_string)
    with open(_path, "r") as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=_fields)
        next(reader)
        for row in reader:
            raw_fips = str(row.get("fips"))
            if len(raw_fips) > 2:
                fips = raw_fips.zfill(6)
                for year in _years:
                    pop = row.get(year)
                    if pop:
                        pop = int(pop.replace(",", ""))
                    else:
                        pop = None
                    session.merge(
                        CountyPopulation(
                            county_id=fips,
                            census_year=int(year),
                            population=pop
                        )
                    )
    session.commit()
    session.close()