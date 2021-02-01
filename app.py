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
            "name": obj.name
        }
    if isinstance(obj, Institute):
        return {
            "id": obj.id,
            "name": obj.name,
            "area_id": obj.area_id,
        }
    if isinstance(obj, Indicator):
        return {
            "id": obj.id,
            "indicator": obj.indicator,
            "value": obj.value,
            "institute_id": obj.institute_id,
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

@app.route('/api/areas', methods=['GET'])
def get_areas():
    return json.dumps(session.query(Area).all(), ensure_ascii=False, default=my_default)

@app.route('/api/indicators', methods=['GET'])
def get_indicators():
    return json.dumps(session.query(Indicator).all(), ensure_ascii=False, default=my_default)

@app.route('/api/year/new', methods=['POST'])
def new_year():
    data = request.get_json()
    areas = data['areas']
    for area in areas:
        is_area_exists = session.query(exists().where(Area.name == area['name'])).scalar()

        current_area = None

        if(not is_area_exists):
            current_area = Area(name=area['name'], year = area['year'])

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
        session.add(current_area)

    session.commit()

    return {'indicators': json.dumps(session.query(Indicator).all(), ensure_ascii=False, default=my_default),
            'institutes': json.dumps(session.query(Institute).all(), ensure_ascii=False, default=my_default),
            'areas': json.dumps(session.query(Area).all(), ensure_ascii=False, default=my_default)}



@app.route('/api/test/new', methods=['POST'])
def post_test():
    area = Area(name="Белгородская область")
    indicators = [
        Indicator(indicator="показатель 1", value="занчение 1"),
        Indicator(indicator="показатель 2", value="занчение 2"),
        Indicator(indicator="показатель 3", value="занчение 3"),
        Indicator(indicator="показатель 4", value="занчение 4")
    ]
    institutes = Institute(name='Автономная некоммерческая организация высшего образования "Белгородский университет кооперации, экономики и права"')


    institutes.indicators = indicators
    area.institutes = [institutes]

    session.add(area)
    session.commit()
    return dict(indicators=json.dumps(session.query(Indicator).all(), ensure_ascii=False, default=my_default),
                institutes=json.dumps(session.query(Institute).all(), ensure_ascii=False, default=my_default),
                areas=json.dumps(session.query(Area).all(), ensure_ascii=False, default=my_default))


if __name__ == '__main__':
    app.debug = True
    app.run(port=4996)
