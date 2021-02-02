import os

from flask import Flask, render_template, request, redirect, url_for, json, jsonify
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from database_setup import *

app = Flask(__name__)

# Подключаемся и создаем сессию базы данных
engine = create_engine(conn_string)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def my_default(obj):
    if isinstance(obj, Area):
        return {
            "id": obj.id,
            "name": obj.name,
            "institutes" : obj.institutes
        }
    if isinstance(obj, Institute):
        return {
            "id": obj.id,
            "name": obj.name,
            "area_id": obj.area_id,
            "indicators" : obj.indicators
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


# страница, которая будет отображать все книги в базе данных
# Эта функция работает в режиме чтения.
@app.route('/api/')
@app.route('/api/areas')
def show_areas():
    areas = session.query(Area).all()
    # newArea = Area(name="Belgorod")
    # session.add(newArea)
    # session.commit()

    return json.dumps(areas, ensure_ascii=False, default=my_default)


# Эта функция позволит создать новую книгу и сохранить ее в базе данных.
@app.route('/api/areas/new', methods=['POST'])
def new_area():
    data = request.get_json()
    new_area = Area(name=data['name'])
    session.add(new_area)
    session.commit()

    return json.dumps(session.query(Area).all(), ensure_ascii=False, default=my_default)


@app.route('/api/institutes/new', methods=['POST'])
def new_institute():
    data = request.get_json()
    institute = Institute(name=data['name'], area_id=data['area_id'])
    indicators = data['indicators']
    institute.indicators = [Indicator(indicator=ind['indicator'], value=ind['value']) for ind in indicators]
    session.add(institute)
    session.commit()

    return {'indicators': json.dumps(session.query(Indicator).all(), ensure_ascii=False, default=my_default),
            'institutes': json.dumps(session.query(Institute).all(), ensure_ascii=False, default=my_default),
            'areas': json.dumps(session.query(Area).all(), ensure_ascii=False, default=my_default)}

@app.route('/api/indicators/new', methods=['POST'])
def new_indicator_and_value():
    data = request.get_json()
    indicator_and_value = Indicator(indicator=data['indicator'], value=data['value'], institute_id = data['institute_id'])
    session.add(indicator_and_value)
    session.commit()

    return json.dumps(session.query(Indicator).all(), ensure_ascii=False, default=my_default)


@app.route('/api/institutes', methods=['GET'])
def get_institutes():
    return json.dumps(session.query(Institute).all(), ensure_ascii=False, default=my_default)

@app.route('/areas', methods=['GET'])
def get_areas():
    areas = session.query(Area).all()
    return render_template("areas.html", areas = areas)

@app.route('/', methods=['GET'])
def get_years():
    years = session.query(Year).all()
    return render_template("years.html", years = years)

@app.route('/year/<int:year_id>', methods=['GET'])
def get_year(year_id):
    areas = session.query(Area).filter_by(year_id = year_id).all()
    year =  session.query(Year).filter_by(id = year_id).one()
    return render_template("areas.html", areas = areas, year = year.year)

@app.route('/year/areas/<int:area_id>', methods=['GET'])
def get_area(area_id):
    institutes = session.query(Institute).filter_by(area_id = area_id).all()
    area = session.query(Area).filter_by(id = area_id).one()
    return render_template("area.html", institutes = institutes, name=area.name)


@app.route('/year/areas/institute/<int:institute_id>', methods=['GET'])
def get_institute(institute_id):
    institute = session.query(Institute).filter_by(id = institute_id).one()
    return render_template("institute.html", institute = institute)


@app.route('/api/indicators', methods=['GET'])
def get_indicators():
    return json.dumps(session.query(Indicator).all(), ensure_ascii=False, default=my_default)


@app.route('/api/year/upload', methods=['POST'])
def new_year_file():
    data = json.loads(request.files['json_data'].read())
    is_year_exists = session.query(exists().where(Year.year == data['year'])).scalar()

    current_year = None

    if (not is_year_exists):
        current_year = Year(year=data['year'])

    else:
        current_year = session.query(Year).filter_by(year=data['year']).one()

    areas_array = []
    areas = data['areas']
    for area in areas:
        is_area_exists = session.query(exists().where(Area.year_id == current_year.id)).scalar()

        current_area = None

        if (not is_area_exists):
            current_area = Area(name=area['name'])
            areas_array.append(current_area)
        else:
            current_area = session.query(Area).filter_by(name=area['name']).one()

        institutes_array = []
        institutes = area['institutes']
        print(f"area {current_area.name}")
        for institute in institutes:
            is_institute_exists = session.query(exists().where(Institute.area_id == current_area.id)).scalar()

            current_institute = None
            if (not is_institute_exists):
                current_institute = Institute(name=institute['name'])
                institutes_array.append(current_institute)
            else:
                current_institute = session.query(Institute).filter_by(name=institute['name']).one()
            print(f"inst {current_institute.name}")
            indicators_array = []
            directions_array = []
            indicators = institute['indicators']
            directions = institute['directions']
            for indicator in indicators:
                is_indicator_exists = session.query(
                    exists().where(Indicator.institute_id == current_institute.id)).scalar()

                current_indicator = None
                if (not is_indicator_exists):
                    current_indicator = Indicator(indicator=indicator["indicator"], value=indicator['value'])
                    indicators_array.append(current_indicator)
                else:
                    current_indicator = session.query(Indicator).filter_by(indicator=indicator['indicator']).one()


            for direction in directions:
                is_direction_exists = session.query(
                    exists().where(Direction.institute_id == current_institute.id)).scalar()

                current_direction = None
                if (not is_direction_exists):
                    current_direction = Direction(direction=direction["direction"])
                    directions_array.append(current_direction)
                else:
                    current_direction = session.query(Direction).filter_by(direction=direction['direction']).one()

            current_institute.indicators += indicators_array
            current_institute.directions += directions_array

        current_area.institutes += institutes_array

    current_year.areas += areas_array
    session.add(current_year)
    session.commit()

    return {'status': "ok"}

@app.route('/api/year/new', methods=['POST'])
def new_year():
    data = request.get_json()
    is_year_exists = session.query(exists().where(Year.year == data['year'])).scalar()

    current_year = None

    if (not is_year_exists):
        current_year = Year(year=data['year'])

    else:
        current_year = session.query(Year).filter_by(year=data['year']).one()

    areas_array = []
    areas = data['areas']
    for area in areas:
        is_area_exists = session.query(exists().where(Area.name == area['name'])).scalar()

        current_area = None

        if(not is_area_exists):
            current_area = Area(name=area['name'])
            areas_array.append(current_area)
        else:
            current_area =session.query(Area).filter_by(name=area['name']).one()

        institutes_array = []
        institutes = area['institutes']
        for institute in institutes:
            is_institute_exists = session.query(exists().where(Institute.name == institute['name'])).scalar()

            current_institute = None
            if (not is_institute_exists):
                current_institute = Institute(name=institute['name'])
                institutes_array.append(current_institute)
            else:
                current_institute = session.query(Institute).filter_by(name=institute['name']).one()

            indicators_array = []
            indicators = institute['indicators']
            for indicator in indicators:
                is_indicator_exists = session.query(exists().where(Indicator.indicator == indicator['indicator'])).scalar()

                current_indicator = None
                if (not is_indicator_exists):
                    current_indicator = Indicator(indicator=indicator["indicator"], value=indicator['value'])
                    indicators_array.append(current_indicator)
                else:
                    current_indicator = session.query(Indicator).filter_by(indicator=indicator['indicator']).one()



            current_institute.indicators += indicators_array

        current_area.institutes += institutes_array

    current_year.areas += areas_array
    session.add(current_year)
    session.commit()

    return {'indicators': json.dumps(session.query(Indicator).all(), ensure_ascii=False, default=my_default),
            'institutes': json.dumps(session.query(Institute).all(), ensure_ascii=False, default=my_default),
            'areas': json.dumps(session.query(Area).all(), ensure_ascii=False, default=my_default)}


@app.route('/api/year/fromfile', methods=['POST'])
def fromfile():
    path = os.path.join(os.getcwd(), "year2019.json")

    file = open(path, "r", encoding="utf-8")
    data = json.loads(file.read())
    file.close()
    is_year_exists = session.query(exists().where(Year.year == data['year'])).scalar()

    current_year = None

    if (not is_year_exists):
        current_year = Year(year=data['year'])

    else:
        current_year = session.query(Year).filter_by(year=data['year']).one()

    areas_array = []
    areas = data['areas']
    for area in areas:
        is_area_exists = session.query(exists().where(Area.name == area['name'])).scalar()

        current_area = None

        if(not is_area_exists):
            current_area = Area(name=area['name'])
            areas_array.append(current_area)
        else:
            current_area =session.query(Area).filter_by(name=area['name']).one()

        institutes_array = []
        institutes = area['institutes']
        for institute in institutes:
            is_institute_exists = session.query(exists().where(Institute.name == institute['name'])).scalar()

            current_institute = None
            if (not is_institute_exists):
                current_institute = Institute(name=institute['name'])
                institutes_array.append(current_institute)
            else:
                current_institute = session.query(Institute).filter_by(name=institute['name']).one()

            indicators_array = []
            directions_array = []
            indicators = institute['indicators']
            directions = institute['directions']
            for indicator in indicators:
                is_indicator_exists = session.query(exists().where(Indicator.indicator == indicator['indicator'])).scalar()

                current_indicator = None
                if (not is_indicator_exists):
                    current_indicator = Indicator(indicator=indicator["indicator"], value=indicator['value'])
                    indicators_array.append(current_indicator)
                else:
                    current_indicator = session.query(Indicator).filter_by(indicator=indicator['indicator']).one()

            for direction in directions:
                is_direction_exists = session.query(exists().where(Direction.direction == direction['direction'])).scalar()

                current_direction = None
                if (not is_direction_exists):
                    current_direction = Direction(direction=direction["direction"])
                    directions_array.append(current_direction)
                else:
                    current_direction = session.query(Direction).filter_by(direction=direction['direction']).one()



            current_institute.indicators += indicators_array
            current_institute.directions += directions_array

        current_area.institutes += institutes_array

    current_year.areas += areas_array
    session.add(current_year)
    session.commit()

    return {'status':"ok"}




if __name__ == '__main__':
    app.debug = True
    app.run(port=4996)
