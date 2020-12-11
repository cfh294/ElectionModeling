#!/usr/bin/env python3
"""
Initialize tables in SQLITE db
"""
import argparse
from models import Base
from sqlalchemy import create_engine
from utils import database_string


def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Provide a connection string to create all needed DB objects.")
        ap.add_argument("-db", "--database", default=database_string, type=str, help="Database connection string.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_

@with_args
def main(args):
    engine = create_engine(args.database, echo=True)
    Base.metadata.create_all(engine)

main()