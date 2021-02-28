from sqlalchemy import Column, ForeignKey, Integer, String, Float

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

conn_string = "postgresql://postgres:root@localhost/t"

Base = declarative_base()


class Year(Base):
    __tablename__ = 'year'

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)

    def __lt__(self, other):
        return self.year < other.year


class Area(Base):
    __tablename__ = 'area'

    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    year_id = Column(Integer, ForeignKey('year.id'))
    year = relationship("Year", backref="areas")


class Institute(Base):
    __tablename__ = 'institute'

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey('area.id'))
    name = Column(String(500), nullable=False)
    area = relationship("Area", backref="institutes")


class Indicator(Base):
    __tablename__ = 'indicators'

    id = Column(Integer, primary_key=True)
    indicator = Column(String(500), nullable=False)
    value = Column(String(500), nullable=False)
    institute_id = Column(Integer, ForeignKey('institute.id'))
    institute = relationship("Institute", backref="indicators")


class Direction(Base):
    __tablename__ = 'direction'

    id = Column(Integer, primary_key=True)
    direction = Column(String(250), nullable=False)
    institute_id = Column(Integer, ForeignKey('institute.id'))
    institute = relationship("Institute", backref="directions")


class AreaSummary(Base):
    __tablename__ = 'area_sum'

    id = Column(Integer, primary_key=True)
    year_id = Column(Integer, ForeignKey('year.id'))
    year = relationship("Year", backref="areas_summary")
    name = Column(String(500), nullable=False)

class Subject(Base):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey('area_sum.id'))
    code = Column(String(500), nullable=False)

    area_summary = relationship("AreaSummary", backref="subjects")

class P211(Base):
    __tablename__ = 'p211'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))
    budget_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    gr_contract_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)
    subject = relationship("Subject", backref="P211")


class P2124(Base):
    __tablename__ = 'p2124'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))
    contract_amount = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)
    subject = relationship("Subject", backref="P2124")

class P213(Base):
    __tablename__ = 'p213'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))
    total_grad_amount = Column(Integer, nullable=True)
    magistracy_amount = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)
    subject = relationship("Subject", backref="P213")


class PostgraduateBachelor(Base):
    __tablename__ = 'postgraduate_bachelor'
    id = Column(Integer, primary_key=True)
    country = Column(String(500), nullable=True)
    row_number = Column(Integer, nullable=True)
    code = Column(Integer, nullable=True)
    accepted_students_amount = Column(Integer, nullable=True)
    a_fed_budget = Column(Float, nullable=True)
    a_rf_budget = Column(Float, nullable=True)
    a_local_budget = Column(Float, nullable=True)
    a_contract_amount = Column(Integer, nullable=True)
    total_students_amount = Column(Integer, nullable=True)
    t_fed_budget = Column(Float, nullable=True)
    t_rf_budget = Column(Float, nullable=True)
    t_local_budget = Column(Float, nullable=True)
    t_contract_amount = Column(Integer, nullable=True)
    grad_students_amount = Column(Integer, nullable=True)
    g_fed_budget = Column(Float, nullable=True)
    g_rf_budget = Column(Float, nullable=True)
    g_local_budget = Column(Float, nullable=True)
    g_contract_amount = Column(Integer)

    # ..
    area_id = Column(Integer, ForeignKey('area_sum.id'))
    area_summary = relationship("AreaSummary", backref="postgraduate_bachelors")

class PostgraduateSpecialty(Base):
    id = Column(Integer, primary_key=True)
    __tablename__ = 'postgraduate_specialty'
    country = Column(String(500), nullable=True)
    row_number = Column(Integer, nullable=True)
    code = Column(Integer, nullable=True)
    accepted_students_amount = Column(Integer, nullable=True)
    a_fed_budget = Column(Float, nullable=True)
    a_rf_budget = Column(Float, nullable=True)
    a_local_budget = Column(Float, nullable=True)
    a_contract_amount = Column(Integer, nullable=True)
    total_students_amount = Column(Integer, nullable=True)
    t_fed_budget = Column(Float, nullable=True)
    t_rf_budget = Column(Float, nullable=True)
    t_local_budget = Column(Float, nullable=True)
    t_contract_amount = Column(Integer, nullable=True)
    grad_students_amount = Column(Integer, nullable=True)
    g_fed_budget = Column(Float, nullable=True)
    g_rf_budget = Column(Float, nullable=True)
    g_local_budget = Column(Float, nullable=True)
    g_contract_amount = Column(Integer)

    # ..
    area_id = Column(Integer, ForeignKey('area_sum.id'))

    area_summary = relationship("AreaSummary", backref="postgraduate_specialists")

class PostgraduateMaster(Base):
    __tablename__ = 'postgraduate_master'
    id = Column(Integer, primary_key=True)
    country = Column(String(500), nullable=True)
    row_number = Column(Integer, nullable=True)
    code = Column(Integer, nullable=True)
    accepted_students_amount = Column(Integer, nullable=True)
    a_fed_budget = Column(Float, nullable=True)
    a_rf_budget = Column(Float, nullable=True)
    a_local_budget = Column(Float, nullable=True)
    a_contract_amount = Column(Integer, nullable=True)
    total_students_amount = Column(Integer, nullable=True)
    t_fed_budget = Column(Float, nullable=True)
    t_rf_budget = Column(Float, nullable=True)
    t_local_budget = Column(Float, nullable=True)
    t_contract_amount = Column(Integer, nullable=True)
    grad_students_amount = Column(Integer, nullable=True)
    g_fed_budget = Column(Float, nullable=True)
    g_rf_budget = Column(Float, nullable=True)
    g_local_budget = Column(Float, nullable=True)
    g_contract_amount = Column(Integer)

    # ..
    area_id = Column(Integer, ForeignKey('area_sum.id'))
    area_summary = relationship("AreaSummary", backref="postgraduate_masters")

engine = create_engine(conn_string)

Base.metadata.create_all(engine)
