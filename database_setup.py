from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

conn_string = "postgresql://my_user:password123@localhost/my_database"

Base = declarative_base()


class AreaName(Base):
    __tablename__ = 'area_name'

    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)


class InstituteName(Base):
    __tablename__ = 'institute_name'

    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)


class Area(Base):
    __tablename__ = 'area'
    year = Column(Integer, nullable=False)
    id = Column(Integer, primary_key=True)

    area_name_id = Column(Integer, ForeignKey('area_name.id'))
    area_name = relationship("AreaName", uselist=False, backref="area_name")


class Institute(Base):
    __tablename__ = 'institute'

    id = Column(Integer, primary_key=True)

    area_id = Column(Integer, ForeignKey('area.id'))
    institute_name_id = Column(Integer, ForeignKey('institute_name.id'))

    area = relationship("Area", backref="institutes")

    institute_name = relationship("InstituteName", uselist=False, backref="institute_name")
    niu = Column(String(500), nullable=True)
    oru = Column(String(500), nullable=True)
    _5100 = Column(String(500), nullable=True)
    iop = Column(String(500), nullable=True)
    psr = Column(String(500), nullable=True)


class Indicator(Base):
    __tablename__ = 'indicators'

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey('institute.id'))

    indicator = Column(String(500), nullable=False)
    value = Column(String(500), nullable=False)

    institute = relationship("Institute", backref="indicators")


class Direction(Base):
    __tablename__ = 'direction'

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey('institute.id'))

    direction = Column(String(250), nullable=False)

    institute = relationship("Institute", backref="directions")


class Subject(Base):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True)
    code = Column(String(500), nullable=False)
    name = Column(String(250), nullable=False)
    area_id = Column(Integer, ForeignKey('area.id'))

    area_summary = relationship("Area", backref="subjects")


class P211(Base):
    __tablename__ = 'p211'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    budget_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    gr_contract_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="P211", uselist=False)


class P2124(Base):
    __tablename__ = 'p2124'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    contract_amount = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="P2124", uselist=False)


class P213(Base):
    __tablename__ = 'p213'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    total_grad_amount = Column(Integer, nullable=True)
    magistracy_amount = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="P213", uselist=False)


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=True)
    name = Column(String(500), nullable=True)


class PostgraduateBachelor(Base):
    __tablename__ = 'postgraduate_bachelor'

    id = Column(Integer, primary_key=True)

    country_id = Column(Integer, ForeignKey('country.id'))
    area_id = Column(Integer, ForeignKey('area.id'))

    row_number = Column(Integer, nullable=True)
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

    area_summary = relationship("Area", backref="postgraduate_bachelors")


class PostgraduateSpecialty(Base):
    __tablename__ = 'postgraduate_specialty'

    id = Column(Integer, primary_key=True)

    country_id = Column(Integer, ForeignKey('country.id'))

    row_number = Column(Integer, nullable=True)
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

    area_id = Column(Integer, ForeignKey('area.id'))
    area_summary = relationship("Area", backref="postgraduate_specialists")


class PostgraduateMaster(Base):
    __tablename__ = 'postgraduate_master'
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('country.id'))

    row_number = Column(Integer, nullable=True)
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

    area_id = Column(Integer, ForeignKey('area.id'))
    area_summary = relationship("Area", backref="postgraduate_masters")


engine = create_engine(conn_string)

Base.metadata.create_all(engine)
