from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

conn_string = "postgresql://postgres:123@localhost/postgres"

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
    code = Column(String(500), nullable=True)
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


class P211_SPO(Base):
    __tablename__ = 'spo_p211'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    str_number = Column(Integer, nullable=True)
    budget_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)
    total_accepted = Column(Integer, nullable=True)
    disabled_accepted = Column(Integer, nullable=True)
    basic_level_amount = Column(Integer, nullable=True)
    advanced_level = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    disabled_fed_amount = Column(Integer, nullable=True)
    total_subject_amount = Column(Integer, nullable=True)
    disabled_subject_amount = Column(Integer, nullable=True)
    local_budget_amount = Column(Float, nullable=True)
    budget_contract_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="P211_SPO", uselist=True)


class P2121_SPO(Base):
    __tablename__ = 'spo_p2121'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    str_number = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="P2121_SPO", uselist=True)


class P2124_SPO(Base):
    __tablename__ = 'spo_p2124'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    total_accepted = Column(Integer, nullable=True)
    disabled_accepted = Column(Integer, nullable=True)
    basic_level_amount = Column(Integer, nullable=True)
    advanced_level = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    disabled_fed_amount = Column(Integer, nullable=True)
    total_subject_amount = Column(Integer, nullable=True)
    disabled_subject_amount = Column(Integer, nullable=True)
    local_budget_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)
    targeted_education = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="P2124_SPO", uselist=True)


class P2141_SPO(Base):
    __tablename__ = 'spo_p2141'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    str_number = Column(Integer, nullable=True)
    serial_number = Column(Integer, nullable=True)
    total_amount = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    total_subject_amount = Column(Integer, nullable=True)
    local_budget_amount = Column(Integer, nullable=True)
    legal_representative_amount = Column(Integer, nullable=True)
    individual_amount = Column(Integer, nullable=True)
    legal_entity_amount = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="P2141_SPO", uselist=True)


class P2142_SPO(Base):
    __tablename__ = 'spo_p2142'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    str_number = Column(Integer, nullable=True)
    code = Column(String(250), nullable=True)
    serial_number = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)
    accelerated_learning = Column(Integer, nullable=True)
    total_disabled_amount = Column(Integer, nullable=True)
    disabled_amount = Column(Integer, nullable=True)
    disabled_children_amount = Column(Integer, nullable=True)
    excepted_disabled = Column(Integer, nullable=True)
    excepted_disabled_children = Column(Integer, nullable=True)
    subject = relationship("Subject", backref="P2142_SPO", uselist=True)


class OldP211_SPO(Base):
    __tablename__ = 'old_spo_p211'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    str_number = Column(Integer, nullable=True)
    applications_submitted = Column(Integer, nullable=True)
    total_accepted = Column(Integer, nullable=True)
    basic_level_amount = Column(Integer, nullable=True)
    advanced_level = Column(Integer, nullable=True)
    fed_accepted = Column(Integer, nullable=True)
    subject_budget_accepted = Column(Integer, nullable=True)
    local_budget_accepted = Column(Integer, nullable=True)
    full_refund = Column(Integer, nullable=True)
    subject = relationship("Subject", backref="old_P211_SPO", uselist=True)


class OldP212_SPO(Base):
    __tablename__ = 'old_spo_p212'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    str_number = Column(Integer, nullable=True)
    total_course_1 = Column(Integer, nullable=True)
    budget_course_1 = Column(Integer, nullable=True)
    total_course_2 = Column(Integer, nullable=True)
    budget_course_2 = Column(Integer, nullable=True)
    total_course_3 = Column(Integer, nullable=True)
    budget_course_3 = Column(Integer, nullable=True)
    total_course_4 = Column(Integer, nullable=True)
    budget_course_4 = Column(Integer, nullable=True)
    total_course_5 = Column(Integer, nullable=True)
    budget_course_5 = Column(Integer, nullable=True)
    total_course_6 = Column(Integer, nullable=True)
    budget_course_6 = Column(Integer, nullable=True)
    total_student_amount = Column(Integer, nullable=True)
    subject = relationship("Subject", backref="old_P212_SPO", uselist=True)


class OldP2122_SPO(Base):
    __tablename__ = 'old_spo_p2122'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    str_number = Column(Integer, nullable=True)
    basic_graduated = Column(Integer, nullable=True)
    advanced_graduated = Column(Integer, nullable=True)
    total_graduated = Column(Integer, nullable=True)
    subject = relationship("Subject", backref="old_P2122_SPO", uselist=True)


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=True)
    name = Column(String(500), nullable=True)


class OldP27_SPO(Base):
    __tablename__ = 'old_spo_p27'

    id = Column(Integer, primary_key=True)

    country_id = Column(Integer, ForeignKey('country.id'))
    area_id = Column(Integer, ForeignKey('area.id'))

    str_number = Column(Integer, nullable=True)
    country_code = Column(Integer, nullable=True)
    total_accepted = Column(Integer, nullable=True)
    fed_budget_accepted = Column(Integer, nullable=True)
    subject_budget_accepted = Column(Integer, nullable=True)
    full_refund_accepted = Column(Integer, nullable=True)
    total_amount = Column(Integer, nullable=True)
    fed_budget_amount = Column(Integer, nullable=True)
    subject_budget_amount = Column(Integer, nullable=True)
    full_refund_amount = Column(Integer, nullable=True)
    total_graduated = Column(Integer, nullable=True)
    fed_budget_graduated = Column(Integer, nullable=True)
    subject_budget_graduated = Column(Integer, nullable=True)
    full_refund_graduated = Column(Integer, nullable=True)

    area_summary = relationship("Area", backref="old_P27_SPO")


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


class OldP211(Base):
    __tablename__ = 'old_p211'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    name = Column(String(500), nullable=False)
    total_amount = Column(Integer, nullable=True)
    total_fed_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="old_P211", uselist=False)


class OldP212(Base):
    __tablename__ = 'old_p212'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    total_fed_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="old_P212", uselist=False)


class OldP212P(Base):
    __tablename__ = 'old_p212p'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    total_fed_amount = Column(Integer, nullable=True)
    contract_amount = Column(Integer, nullable=True)
    women_amount = Column(Integer, nullable=True)

    subject = relationship("Subject", backref="old_P212P", uselist=False)


class OldP210(Base):
    __tablename__ = 'old_p210'
    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey('area.id'))

    country_id = Column(Integer, ForeignKey('country.id'))
    row_number = Column(Integer, nullable=True)
    accepted_students_amount = Column(Integer, nullable=True)
    a_fed_budget = Column(Integer, nullable=True)
    a_rf_budget = Column(Integer, nullable=True)
    total_students_amount = Column(Integer, nullable=True)
    t_fed_budget = Column(Integer, nullable=True)
    t_rf_budget = Column(Integer, nullable=True)
    grad_students_amount = Column(Integer, nullable=True)
    g_fed_budget = Column(Integer, nullable=True)
    g_rf_budget = Column(Integer, nullable=True)

    area_id = Column(Integer, ForeignKey('area.id'))
    area_summary = relationship("Area", backref="old_P210")


class OldP25(Base):
    __tablename__ = 'old_p25'
    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey('area.id'))

    name = Column(String(500), nullable=False)
    amount = Column(Integer, nullable=True)

    area_id = Column(Integer, ForeignKey('area.id'))
    area_summary = relationship("Area", backref="old_P25")


engine = create_engine(conn_string)

Base.metadata.create_all(engine)
