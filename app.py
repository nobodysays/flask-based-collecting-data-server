from flask import Flask, render_template, request, json
from sqlalchemy import exists, and_
from sqlalchemy.orm import sessionmaker
from database_setup import *

app = Flask(__name__)

engine = create_engine(conn_string)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def parsing_default(obj):
    if isinstance(obj, Area):
        return {
            "id": obj.id,
            "name": obj.name,
            "institutes": obj.institutes
        }
    if isinstance(obj, Institute):
        return {
            "id": obj.id,
            "name": obj.name,
            "area_id": obj.area_id,
            "indicators": obj.indicators
        }
    if isinstance(obj, Indicator):
        return {
            "id": obj.id,
            "indicator": obj.indicator,
            "value": obj.value,
            "institute_id": obj.institute_id,

        }
    if isinstance(obj, Year):
        return {
            "id": obj.id,
            "year": obj.year,
            "areas": obj.areas,
        }
    if isinstance(obj, Direction):
        return {
            "id": obj.id,
            "direction": obj.direction,
            "institute_id": obj.institute_id,
        }


@app.route('/areas', methods=['GET'])
def get_areas():
    areas = session.query(Area).all()
    return render_template("areas.html", areas=areas)


@app.route('/', methods=['GET'])
def get_years():
    years = session.query(Year).all()
    return render_template("years.html", years=years)


@app.route('/year/<int:year_id>', methods=['GET'])
def get_year(year_id):
    areas = session.query(Area).filter_by(year_id=year_id).all()
    year = session.query(Year).filter_by(id=year_id).one()
    return render_template("areas.html", areas=areas, year=year.year)


@app.route('/year/areas/<int:area_id>', methods=['GET'])
def get_area(area_id):
    institutes = session.query(Institute).filter_by(area_id=area_id).all()
    area = session.query(Area).filter_by(id=area_id).one()
    return render_template("area.html", institutes=institutes, name=area.name)


@app.route('/year/areas/institute/<int:institute_id>', methods=['GET'])
def get_institute(institute_id):
    institute = session.query(Institute).filter_by(id=institute_id).one()
    return render_template("institute.html", institute=institute)


@app.route('/api/year/upload', methods=['POST'])
def upload_year():
    data = json.loads(request.files['json_data'].read())
    return add_to_bd(data)

@app.route('/api/year/upload/force', methods=['POST'])
def upload_year_force():
    data = json.loads(request.files['json_data'].read())
    return add_to_bd_force(data)

@app.route('/api/year/new', methods=['POST'])
def new_year():
    data = request.get_json()
    return add_to_bd(data)

@app.route('/api/year/new/force', methods=['POST'])
def new_year_force():
    data = request.get_json()
    return add_to_bd_force(data)

def add_to_bd_force(data):
    current_year = Year(year=data['year'])
    areas_array = list()
    areas = data['areas']
    for area in areas:
        current_area = Area(name=area['name'])
        areas_array.append(current_area)
        institutes_array = list()
        institutes = area['institutes']
        print(f"area {current_area.name}")
        for institute in institutes:

            current_institute = Institute(name=institute['name'])
            institutes_array.append(current_institute)
            print(f"inst {current_institute.name}")
            indicators_array = list()
            directions_array = list()
            indicators = institute['indicators']
            directions = institute['directions']
            for indicator in indicators:
                current_indicator = Indicator(indicator=indicator["indicator"], value=indicator['value'])
                indicators_array.append(current_indicator)

            for direction in directions:
                current_direction = Direction(direction=direction["direction"])
                directions_array.append(current_direction)

            current_institute.indicators += indicators_array
            current_institute.directions += directions_array

        current_area.institutes += institutes_array

    current_year.areas += areas_array
    print("commiting to db")
    session.add(current_year)
    session.commit()

    return "ok"
#TODO: оптимизировать
def add_to_bd(data):
    current_year = session.query(Year).filter(Year.year==data['year']).all()
    if len(current_year) == 0:
        current_year = Year(year=data['year'])
    else:
        current_year = current_year[0]

    areas_array = list()
    areas = data['areas']
    for area in areas:

        current_area = session.query(Area).filter(and_(Area.name==area['name'], Area.year_id == current_year.id)).all()

        if len(current_area) == 0:
            current_area = Area(name=area['name'])
            areas_array.append(current_area)
        else:
            current_area = current_area[0]

        institutes_array = list()
        institutes = area['institutes']
        print(f"area {current_area.name}")
        for institute in institutes:

            current_institute = session.query(Institute).filter(and_(Institute.name==institute['name'], Institute.area_id == current_area.id)).all()
            if len(current_institute) ==0:
                current_institute = Institute(name=institute['name'])
                institutes_array.append(current_institute)
            else:
                current_institute = current_institute[0]

            print(f"inst {current_institute.name}")
            indicators_array = list()
            directions_array = list()
            indicators = institute['indicators']
            directions = institute['directions']
            for indicator in indicators:
                current_indicator = session.query(Indicator).filter(and_(Indicator.institute_id == current_institute.id, Indicator.indicator==indicator['indicator'])).all()

                if len(current_indicator) == 0:
                    current_indicator = Indicator(indicator=indicator["indicator"], value=indicator['value'])
                    indicators_array.append(current_indicator)


            for direction in directions:
                current_direction = session.query(Direction).filter(and_(Direction.institute_id == current_institute.id, Direction.direction == direction['direction'])).all()
                if len(current_direction) == 0:
                    current_direction = Direction(direction=direction["direction"])
                    directions_array.append(current_direction)


            current_institute.indicators += indicators_array
            current_institute.directions += directions_array

        current_area.institutes += institutes_array

    current_year.areas += areas_array

    session.add(current_year)
    session.commit()

    return "ok"

if __name__ == '__main__':
    app.debug = True
    app.run(port=4996)
