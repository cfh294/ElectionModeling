#!/usr/bin/env python3
"""
Load geographic county data into SQLITE db
"""
import fiona
import shapely
import pathlib
import argparse
from utils import get_session, database_string
from models import CountyGeography

_path = str(pathlib.PurePath(".", "spatial-data", "counties", "county.shp"))

def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Load geographic info about counties.")
        ap.add_argument("-p", "--path", default=_path, help="Path to counties shapefile.")
        ap.add_argument("-c", "--connection", default=database_string)
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_

@with_args
def main(args):
    session = get_session(args.connection)
    for county in fiona.open(args.path):
        props = county.get("properties")
        a_water = props.get("AWATER")
        a_land = props.get("ALAND")
        fips = str(props.get("GEOID")).zfill(6)
        geom = county.get("geometry")
        coordinates = geom.get("coordinates")
        num_verts = 0
        if geom.get("type") == "Polygon":
            for line in coordinates:
                num_verts += len(line)
        else:
            for polygon in coordinates:
                for line in polygon:
                    num_verts += len(line)
        session.merge(
            CountyGeography(
                county_id=fips, 
                area_water=a_water,
                area_land=a_land,
                vertex_count=num_verts
            )
        )

    session.commit()


if __name__ == "__main__":
    main()



