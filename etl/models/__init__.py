"""
SQLAlchemy models
"""
import datetime
import argparse
from sqlalchemy import BLOB, Boolean, Column, String, Integer, Float, DateTime, Date, create_engine, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class State(Base):
    __tablename__ = "state"
    id = Column(String(6), primary_key=True, nullable=False)
    code = Column(String(2), nullable=False)
    name = Column(String(30), nullable=False)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    counties = relationship("County", back_populates="state")
    candidates = relationship("Candidate", back_populates="home_state")
    __table_args__ = (UniqueConstraint("code", name="uix_state"),)


class County(Base):
    __tablename__ = "county"
    id = Column(String(6), primary_key=True, nullable=False)
    state_id = Column(String(6), ForeignKey("state.id"), nullable=False)
    state = relationship("State", back_populates="counties")
    name = Column(String(255), nullable=False)
    vote_results = relationship("CountyVoteResult", back_populates="county")
    geography = relationship("CountyGeography", back_populates="county")
    upload_datetime = Column(DateTime, default=datetime.datetime.now())


class PoliticalParty(Base):
    __tablename__ = "political_party"
    id = Column(Integer, primary_key=True)
    code = Column(String(3), nullable=False)
    name = Column(String(100), nullable=False)
    founding_year = Column(Integer)
    campaigns = relationship("Campaign", back_populates="political_party")
    defunct_ind = Column(Boolean, default=False, nullable=False)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("code", name="uix_political_party"),)


class Candidate(Base):
    __tablename__ = "candidate"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(40), nullable=False)
    middle_initial = Column(String(1))
    last_name = Column(String(40), nullable=False)
    birth_date = Column(Date)
    death_date = Column(Date)
    nickname = Column(String(40))
    display_name = Column(String(255))
    home_state_id = Column(String(6), ForeignKey("state.id")) 
    home_state = relationship("State", back_populates="candidates")
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("first_name", "last_name", "birth_date", name="uix_candidate"),)


class ElectionType(Base):
    __tablename__ = "election_type"
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(255), nullable=False)
    elections = relationship("Election", back_populates="election_type")
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("code", name="uix_election_type"),)


class Election(Base):
    __tablename__ = "election"
    id = Column(Integer, primary_key=True, nullable=False)
    year = Column(Integer, nullable=False)
    election_date = Column(Date)
    election_type_id = Column(Integer, ForeignKey("election_type.id"), nullable=False)
    election_type = relationship("ElectionType", back_populates="elections")
    campaigns = relationship("Campaign", back_populates="election")
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("year", "election_type_id", name="uix_election"),)


class Campaign(Base):
    __tablename__ = "campaign"
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidate.id"), nullable=False)
    candidate = relationship("Candidate", backref="campaigns", foreign_keys=[candidate_id])
    running_mate_id = Column(Integer, ForeignKey("candidate.id"))
    running_mate = relationship("Candidate", backref="vp_campaigns", foreign_keys=[running_mate_id])
    political_party_id = Column(Integer, ForeignKey("political_party.id"), nullable=False)
    political_party = relationship("PoliticalParty", back_populates="campaigns")
    election_id = Column(Integer, ForeignKey("election.id"), nullable=False)
    election = relationship("Election", back_populates="campaigns")
    county_vote_results = relationship("CountyVoteResult", back_populates="campaign")
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("election_id", "candidate_id", "political_party_id", name="uix_campaign"),)


class CountyVoteResult(Base):
    __tablename__ = "county_vote_result"
    id = Column(Integer, primary_key=True)
    county_id = Column(String(6), ForeignKey("county.id"), nullable=False)
    county = relationship("County", back_populates="vote_results")
    campaign_id = Column(Integer, ForeignKey("campaign.id"), nullable=False)
    campaign = relationship(Campaign, back_populates="county_vote_results")
    votes = Column(Integer, nullable=False)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("campaign_id", "county_id", name="uix_cvr"),)


class CountyGeography(Base):
    __tablename__ = "county_geography"
    id = Column(Integer, primary_key=True)
    county_id = Column(String(6), ForeignKey("county.id"), nullable=False)
    county = relationship("County", back_populates="geography")
    area_water = Column(Float, nullable=False)
    area_land = Column(Float, nullable=False)
    vertex_count = Column(Integer, nullable=False)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("county_id", name="uix_cgeog"),)


class CountyPopulation(Base):
    __tablename__ = "county_population"
    id = Column(Integer, primary_key=True)
    county_id = Column(String(6), ForeignKey("county.id"), nullable=False)
    county = relationship("County")
    census_year = Column(Integer, nullable=False)
    population = Column(Integer)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("county_id", "census_year", name="uix_cpop"),)


class CountyPovertyStatistic(Base):
    __tablename__ = "county_poverty_statistic"
    id = Column(Integer, primary_key=True)
    county_id = Column(String(6), ForeignKey("county.id"), nullable=False)
    county = relationship("County")
    year = Column(Integer, nullable=False)
    poverty_rate = Column(Float)
    people_in_poverty = Column(Integer)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("county_id", "year", name="uix_cps"),)


class CountyHealthInsuranceStatistic(Base):
    __tablename__ = "county_health_insurance_statistic"
    id = Column(Integer, primary_key=True)
    county_id = Column(String(6), ForeignKey("county.id"), nullable=False)
    county = relationship("County")
    year = Column(Integer, nullable=False)
    uninsured = Column(Integer)
    uninsured_pct = Column(Float)
    insured = Column(Integer)
    insured_pct = Column(Float)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("county_id", "year", name="uix_chis"),)


class ModelCode(Base):
    __tablename__ = "model_code"
    id = Column(String(50), nullable=False, primary_key=True)
    description = Column(String(100), nullable=False)
    models = relationship("Model", back_populates="model_code")
    drop_cols = relationship("ModelDropCol", back_populates="model_code")
    where_clauses = relationship("ModelWhereClause", back_populates="model_code")


class Model(Base):
    __tablename__ = "model"
    id = Column(Integer, primary_key=True)
    model_code_id = Column(String(50), ForeignKey("model_code.id"),  nullable=False)
    model_code = relationship("ModelCode", back_populates="models")
    model_object = Column(BLOB)
    accuracy = Column(Float)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("model_code_id", name="uix_mod"),)


class ModelDropCol(Base):
    __tablename__ = "model_drop_col"
    id = Column(Integer, primary_key=True)
    model_code_id = Column(String(50), ForeignKey("model_code.id"), nullable=False)
    model_code = relationship("ModelCode", back_populates="drop_cols")
    column = Column(String(50), nullable=False)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("model_code_id", "column", name="uix_mdc"),)


class ModelWhereClause(Base):
    __tablename__ = "model_where_clause"
    id = Column(Integer, primary_key=True)
    model_code_id = Column(String(50), ForeignKey("model_code.id"), nullable=False)
    model_code = relationship("ModelCode", back_populates="where_clauses")
    sql = Column(String(100), nullable=False)
    upload_datetime = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("model_code_id", "sql", name="uix_mwc"),)