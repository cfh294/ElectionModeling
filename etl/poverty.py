#!/usr/bin/env python3
"""
Load poverty data into SQLITE

Data cleaned and csv'd from this original Excel data tool:
https://www.census.gov/library/visualizations/time-series/demo/census-poverty-tool.html
"""
import pathlib
import csv
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CountyPovertyStatistic, County, State

in_path = str(pathlib.Path(".", "base-data", "poverty-raw.csv"))
out_path = str(pathlib.Path(".", "base-data", "poverty.csv"))
in_cols = ["fips","pr_1960","pr_1970","pr_1980","pr_1990","pr_2000","pr_2010","pop_1960","pop_1970","pop_1980","pop_1990","pop_2000","pop_2010","pip_1960","pip_1970","pip_1980","pip_1990","pip_2000","pip_2010"]
out_cols = ["fips", "year", "pr", "pip", "pop"]
years = ["1960", "1970", "1980", "1990", "2000", "2010"]


def get_cols_by_year(in_row, in_year):
    fips = str(in_row.get("fips"))
    if len(fips) <= 2:
        fips = fips.zfill(3)
        fips = fips + "0"*(6-len(fips))
    else:
        fips = fips.zfill(6)
    out_vals = { "fips" : fips, "year" : in_year }
    for key, value in in_row.items():
        if in_year in key:
            new_key = key.split("_")[0]
            if value:
                if new_key == "pr":
                    out_vals[new_key] = float(value)
                else:
                    new_val = value.replace(",", "")
                    out_vals[new_key] = int(new_val)
            else:
                out_vals[new_key] = ""
    return out_vals

def generate_cleaned_csv(in_rows):
    with open(out_path, "w") as csv_file:   
        writer = csv.DictWriter(csv_file, fieldnames=out_cols)
        writer.writeheader()
        writer.writerows(in_rows)

def to_db(new_row, session, fips_to_county, fips_to_state):
    fips = new_row.get("fips")
    create_args = {}
    if fips in fips_to_county:
        model = CountyPovertyStatistic        
        create_args["county"] = fips_to_county[fips]
    elif fips in fips_to_state:
        pass  # no longer supported/needed
    else:
        county = session.query(County).filter_by(id=fips).first()
        if county:
            fips_to_county[fips] = county
            model = CountyPovertyStatistic        
            create_args["county"] = county
        else:
            state = session.query(State).filter_by(id=fips).first()
            if state:
                fips_to_state[fips] = state
                model = StatePovertyStatistic
                create_args["state"] = state
            else:
                model = None
    if model:
        create_args["year"] = int(new_row.get("year"))
        create_args["poverty_rate"] = new_row.get("pr")
        create_args["people_in_poverty"] = new_row.get("pip")
        session.merge(model(**create_args))


def cmd_line(f):
    def wrap(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Load the 2020 federal election json file to a database.")
        ap.add_argument("-db", "--database", action="store_true", required=False, help="Specify if you would like to insert to the database.")
        ap.add_argument("-c", "--connection", default="sqlite:///election.db", help="Database connection string.", type=str)
        ap.add_argument("-o", "--output", action="store_true", required=False, help="Specify if you want to output a .csv file with the new, tidy data.")
        return f(ap.parse_args(), *args, **kwargs)
    return wrap

@cmd_line
def main(args):
    csv_rows = []
    fips_to_county = {}
    fips_to_state = {}
    session = sessionmaker(create_engine(args.connection))()
    with open(in_path, "r") as in_csv:
        reader = csv.DictReader(in_csv, fieldnames=in_cols)

        # write header in out-file, skip header in in-file
        next(reader)
        for row in reader:
            for year in years:
                new_row = get_cols_by_year(row, year)
                if args.database:
                    to_db(new_row, session, fips_to_county, fips_to_state)
                csv_rows.append(new_row)

    if args.output:
        generate_cleaned_csv(csv_rows)
    session.commit()

if __name__ == "__main__":
    main()
