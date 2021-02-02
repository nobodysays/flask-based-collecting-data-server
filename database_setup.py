from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

conn_string = "postgresql://postgres:root@localhost/test9"

Base = declarative_base()


class Year(Base):
    __tablename__ = 'year'

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)


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


engine = create_engine(conn_string)

Base.metadata.create_all(engine)
