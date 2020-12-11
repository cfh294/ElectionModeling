"""
Some utility functions
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Election, ElectionType, PoliticalParty, Campaign

database_string = "sqlite:///election.db"

def get_session(cnxn_string):
    return sessionmaker(
        create_engine(cnxn_string)
    )()


def get_campaign(session, year, party_id, election_type="PRESIDENTIAL", cand_name=None):
    election = session.query(Election).filter_by(
        election_type=session.query(ElectionType).filter_by(code=election_type).first(),
        year=year
    ).first()
    pp = session.query(PoliticalParty).filter_by(code=party_id).first()
    return session.query(Campaign).filter_by(
        political_party=pp,
        election=election
    ).first()