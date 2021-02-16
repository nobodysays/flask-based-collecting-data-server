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
    return render_template("years.html", years=sorted(years, key=lambda x: x.year, reverse=True))


@app.route('/year/<int:year_id>', methods=['GET'])
def get_year(year_id):
    areas = session.query(Area).filter_by(year_id=year_id).all()
    year = session.query(Year).filter_by(id=year_id).one()
    return render_template("areas.html", areas=sorted(areas, key=lambda x: x.name), year=year.year)


@app.route('/year/areas/<int:area_id>', methods=['GET'])
def get_area(area_id):
    institutes = session.query(Institute).filter_by(area_id=area_id).all()
    area = session.query(Area).filter_by(id=area_id).one()
    return render_template("area.html", institutes=sorted(institutes, key=lambda x: x.name), name=area.name)


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


@app.route('/api/institute/<int:institute_id>/delete', methods=['POST'])
def delete_institute(institute_id):
    for direction in session.query(Direction).filter_by(institute_id=institute_id).all():
        session.delete(direction)
    for indicator in session.query(Indicator).filter_by(institute_id=institute_id).all():
        session.delete(indicator)
    session.delete(session.query(Institute).filter_by(id=institute_id).one())
    session.commit()
    return "ok"


@app.route('/api/area/<int:area_id>/delete', methods=['POST', 'GET'])
def delete_area(area_id):
    for institute in session.query(Institute).filter_by(area_id=area_id).all():
        delete_institute(institute.id)

    session.delete(session.query(Area).filter_by(id=area_id).one())
    session.commit()
    return "ok"


@app.route('/api/year/<int:year_id>/delete', methods=['POST', 'GET'])
def delete_year(year_id):
    for area in session.query(Area).filter_by(year_id=year_id).all():
        delete_area(area.id)

    session.delete(session.query(Year).filter_by(id=year_id).one())
    session.commit()
    return "ok"


def add_year_summary_to_bd_force(data):
    current_year = Year(year=data['year'])
    data_areas = data['areas']
    areas = list()
    for data_area in data_areas:
        current_area = AreaSummary(name=data_area['name'])
        data_subjects = data_area['subjects']
        data_bachelors = data_area['bachelor']
        data_masters = data_area['magistracy']
        data_specialists = data_area['spec']
        subjects = list()
        bachelors = list()
        masters = list()
        specialists = list()
        for data_subject in data_subjects:
            current_subject = Subject(code=data_subject['code'])
            current_p211 = P211()
            data_current_p211 = data_subject['p211']
            current_p211.budget_amount = data_current_p211['budget_amount']
            current_p211.contract_amount = data_current_p211['contract_amount']
            current_p211.total_fed_amount = data_current_p211['total_fed_amount']
            current_p211.gr_contract_amount = data_current_p211['gr_contract_amount']
            current_p211.women_amount = data_current_p211['women_amount']

            current_p2124 = P2124()
            data_current_p2124 = data_subject['p2124']
            current_p2124.budget_amount = data_current_p2124['budget_amount']
            current_p2124.contract_amount = data_current_p2124['contract_amount']
            current_p2124.total_fed_amount = data_current_p2124['total_fed_amount']
            current_p2124.gr_contract_amount = data_current_p2124['gr_contract_amount']
            current_p2124.women_amount = data_current_p2124['women_amount']

            current_p213 = P213()
            data_current_p213 = data_subject['p2124']
            current_p213.budget_amount = data_current_p213['budget_amount']
            current_p213.contract_amount = data_current_p213['contract_amount']
            current_p213.total_fed_amount = data_current_p213['total_fed_amount']
            current_p213.gr_contract_amount = data_current_p213['gr_contract_amount']
            current_p213.women_amount = data_current_p213['women_amount']

            current_subject.P211 = [current_p211]
            current_subject.P2124 = [current_p2124]
            current_subject.P213 = [current_p213]

            subjects.append(current_subject)

        for data_bachelor in data_bachelors:
            current_bachelor = PostgraduateBachelor()
            current_bachelor.country = data_bachelor['country']
            current_bachelor.row_number = data_bachelor['row_number']
            current_bachelor.code = data_bachelor['code']
            current_bachelor.accepted_students_amount = data_bachelor['accepted_students_amount']
            current_bachelor.a_fed_budget = data_bachelor['a_fed_budget']
            current_bachelor.a_rf_budget = data_bachelor['a_rf_budget']
            current_bachelor.a_local_budget = data_bachelor['a_local_budget']
            current_bachelor.a_contract_amount = data_bachelor['a_contract_amount']
            current_bachelor.total_students_amount = data_bachelor['total_students_amount']
            current_bachelor.t_fed_budget = data_bachelor['t_fed_budget']
            current_bachelor.t_rf_budget = data_bachelor['t_rf_budget']
            current_bachelor.t_local_budget = data_bachelor['t_local_budget']
            current_bachelor.t_contract_amount = data_bachelor['t_contract_amount']
            current_bachelor.grad_students_amount = data_bachelor['grad_students_amount']
            current_bachelor.g_fed_budget = data_bachelor['g_fed_budget']
            current_bachelor.g_rf_budget = data_bachelor['g_rf_budget']
            current_bachelor.g_local_budget = data_bachelor['g_local_budget']
            current_bachelor.g_contract_amount = data_bachelor['g_contract_amount']
            bachelors.append(current_bachelor)

        for data_master in data_masters:
            current_master = PostgraduateMaster()
            current_master.country = data_master['country']
            current_master.row_number = data_master['row_number']
            current_master.code = data_master['code']
            current_master.accepted_students_amount = data_master['accepted_students_amount']
            current_master.a_fed_budget = data_master['a_fed_budget']
            current_master.a_rf_budget = data_master['a_rf_budget']
            current_master.a_local_budget = data_master['a_local_budget']
            current_master.a_contract_amount = data_master['a_contract_amount']
            current_master.total_students_amount = data_master['total_students_amount']
            current_master.t_fed_budget = data_master['t_fed_budget']
            current_master.t_rf_budget = data_master['t_rf_budget']
            current_master.t_local_budget = data_master['t_local_budget']
            current_master.t_contract_amount = data_master['t_contract_amount']
            current_master.grad_students_amount = data_master['grad_students_amount']
            current_master.g_fed_budget = data_master['g_fed_budget']
            current_master.g_rf_budget = data_master['g_rf_budget']
            current_master.g_local_budget = data_master['g_local_budget']
            current_master.g_contract_amount = data_master['g_contract_amount']
            masters.append(current_master)

        for data_specialist in data_specialists:
            current_specialist = PostgraduateSpecialty()
            current_specialist.country = data_specialist['country']
            current_specialist.row_number = data_specialist['row_number']
            current_specialist.code = data_specialist['code']
            current_specialist.accepted_students_amount = data_specialist['accepted_students_amount']
            current_specialist.a_fed_budget = data_specialist['a_fed_budget']
            current_specialist.a_rf_budget = data_specialist['a_rf_budget']
            current_specialist.a_local_budget = data_specialist['a_local_budget']
            current_specialist.a_contract_amount = data_specialist['a_contract_amount']
            current_specialist.total_students_amount = data_specialist['total_students_amount']
            current_specialist.t_fed_budget = data_specialist['t_fed_budget']
            current_specialist.t_rf_budget = data_specialist['t_rf_budget']
            current_specialist.t_local_budget = data_specialist['t_local_budget']
            current_specialist.t_contract_amount = data_specialist['t_contract_amount']
            current_specialist.grad_students_amount = data_specialist['grad_students_amount']
            current_specialist.g_fed_budget = data_specialist['g_fed_budget']
            current_specialist.g_rf_budget = data_specialist['g_rf_budget']
            current_specialist.g_local_budget = data_specialist['g_local_budget']
            current_specialist.g_contract_amount = data_specialist['g_contract_amount']
            specialists.append(current_specialist)

        current_area.subjects += subjects
        current_area.postgraduate_bachelors += bachelors
        current_area.postgraduate_masters += masters
        current_area.postgraduate_specialists += specialists
        areas.append(current_area)
    current_year.areas_summary += areas
    print("commiting to db")
    session.add(current_year)
    session.commit()
    return "ok"


@app.route('/api/yearsummary/upload/force', methods=['POST', 'GET'])
def new_yearsummary():
    data = json.loads(request.files['json_data'].read())
    return add_year_summary_to_bd_force(data)


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


def add_to_bd(data):
    current_year = session.query(Year).filter(Year.year == data['year']).all()
    if len(current_year) == 0:
        current_year = Year(year=data['year'])
    else:
        current_year = current_year[0]

    areas_array = list()
    areas = data['areas']
    for area in areas:

        current_area = session.query(Area) \
            .filter(
            and_(Area.name == area['name'], Area.year_id == current_year.id)) \
            .all()

        if len(current_area) == 0:
            current_area = Area(name=area['name'])
            areas_array.append(current_area)
        else:
            current_area = current_area[0]

        institutes_array = list()
        institutes = area['institutes']
        print(f"area {current_area.name}")
        for institute in institutes:

            current_institute = session.query(Institute) \
                .filter(
                and_(Institute.name == institute['name'], Institute.area_id == current_area.id)) \
                .all()
            if len(current_institute) == 0:
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
                current_indicator = session.query(Indicator) \
                    .filter(
                    and_(Indicator.institute_id == current_institute.id, Indicator.indicator == indicator['indicator'])) \
                    .all()

                if len(current_indicator) == 0:
                    current_indicator = Indicator(indicator=indicator["indicator"], value=indicator['value'])
                    indicators_array.append(current_indicator)

            for direction in directions:
                current_direction = session.query(Direction) \
                    .filter(
                    and_(Direction.institute_id == current_institute.id, Direction.direction == direction['direction'])) \
                    .all()
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
    app.run()
