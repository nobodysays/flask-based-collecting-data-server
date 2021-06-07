import os

from flask import Flask, render_template, request, json
from sqlalchemy import exists, and_
from sqlalchemy.orm import sessionmaker
from database_setup import *

engine = create_engine(conn_string)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


class MyFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                read_json_old_spo()
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__)


@app.route('/areas', methods=['GET'])
def get_areas():
    areas = session.query(Area).all()
    return render_template("areas.html", areas=areas)


@app.route('/year/<int:year>/areas/general/<int:area_id>', methods=['GET'])
def get_area_summary(year, area_id):
    area = session.query(Area).filter(and_(Area.id == area_id, Area.year == year)).one()
    return render_template("summary_area.html", area=area)


@app.route('/', methods=['GET'])
def get_years():
    areas = session.query(Area).all()
    # сначала находим все варианты годов, потом удаляем повторяющиеся
    years = set([area.year for area in areas])

    return render_template("years.html", years=years)


@app.route('/year/<int:year>', methods=['GET'])
def get_year(year):
    areas = session.query(Area).filter_by(year=year).all()
    return render_template("areas.html", areas=areas, year=year)


@app.route('/year/<int:year>/areas/<int:area_id>', methods=['GET'])
def get_area(year, area_id):
    institutes = session.query(Institute).filter_by(area_id=area_id).all()
    area_name = session.query(Area).filter_by(id=area_id).one().area_name.name
    return render_template("area.html", area_id=area_id, institutes=institutes, name=area_name)


@app.route('/year/<int:year>/areas/<int:area_id>/institute/<int:institute_id>', methods=['GET'])
def get_institute(year, area_id, institute_id):
    institute = session.query(Institute).filter_by(id=institute_id).one()
    return render_template("institute.html", institute=institute)


# TODO: необходимо доделать удаление университета
@app.route('/api/institute/<int:institute_id>/delete', methods=['POST'])
def delete_institute(institute_id):
    for direction in session.query(Direction).filter_by(institute_id=institute_id).all():
        session.delete(direction)
    for indicator in session.query(Indicator).filter_by(institute_id=institute_id).all():
        session.delete(indicator)
    session.delete(session.query(Institute).filter_by(id=institute_id).one())
    session.commit()
    return "ok"


# TODO: необходимо доделать удаление
@app.route('/api/area/<int:area_id>/delete', methods=['POST', 'GET'])
def delete_area(area_id):
    for institute in session.query(Institute).filter_by(area_id=area_id).all():
        delete_institute(institute.id)

    session.delete(session.query(Area).filter_by(id=area_id).one())
    session.commit()
    return "ok"


@app.route('/api/year/upload', methods=['POST', 'GET'])
def new_year():
    json_data = json.loads(request.files['json_data'].read())
    areas = session.query(AreaName).all()
    institutes = session.query(InstituteName).all()

    area_names = [area.name.upper() for area in areas]
    institute_names = [institute.name.upper() for institute in institutes]
    # доьавление новых названий областей и университетов
    for area_data in json_data['areas']:
        area_name = area_data['name'].upper()
        if area_name not in area_names:
            temp = AreaName(name=area_name)
            session.add(temp)
            area_names.append(temp)

        for institute_data in area_data['institutes']:
            institute_name = institute_data['name'].upper()
            if institute_name not in institute_names:
                temp = InstituteName(name=institute_name.upper())
                session.add(temp)
                institute_names.append(temp)
    session.commit()
    # извлекаем обновленные данные
    institutes = session.query(InstituteName).all()
    areas = session.query(AreaName).all()

    for area_data in json_data['areas']:
        area_name = area_data['name'].upper()
        print(area_name)
        area_name_id = find_element_by_name(areas, area_name).id
        current_area = Area(area_name_id=area_name_id, year=json_data['year'])
        for institute_data in area_data['institutes']:
            institute_name = institute_data['name'].upper()
            print(institute_name)
            institute_name_id = find_element_by_name(institutes, institute_name).id
            current_institute = Institute(institute_name_id=institute_name_id)
            for indicator_data in institute_data['indicators']:
                current_institute.indicators.append(
                    Indicator(indicator=indicator_data['indicator'], value=indicator_data['value']))

            for direction_data in institute_data["directions"]:
                current_institute.directions.append(Direction(direction=direction_data['direction']))

            current_area.institutes.append(current_institute)
        session.add(current_area)
    print("COMMITING")
    session.commit()
    return "ok"


@app.route('/api/year/spo_upload', methods=['POST', 'GET'])
def new_year_spo():
    base_dir = "C:\\Users\\protuberanzen\\PycharmProjects\\collecting-data\\vpo\\shortSpo\\"

    for file in os.listdir(base_dir):
        print(file)
        json_path = os.path.join(base_dir, file)
        with open(json_path, encoding='utf8') as json_file:
            json_data = json.load(json_file)
        area_names = [area.name.upper() for area in session.query(AreaName).all()]
        # добавляем области
        for area in json_data['areas']:
            area_name = area['name'].upper()
            if area_name not in area_names:
                session.add(AreaName(name=area_name))
                area_names.append(area_name)

        # заносим изменения в базу данных
        session.commit()

        # извлекаем уже обновленные данные из бд
        area_names = session.query(AreaName).all()
        areas = session.query(Area).all()
        subjects = session.query(Subject).all()

        year = json_data['year']
        for area_data in json_data['areas']:
            area_name = area_data['name'].upper()
            print(area_name)
            area = None
            found = False

            # находим область по названию и году
            for с in areas:
                name = с.area_name.name
                if name == area_name:
                    if с.year == int(year):
                        area = с
                        found = True
                        break
                    else:
                        area_name_id = find_element_by_name(area_names, area_name).id
                        area = Area(year=year, area_name_id=area_name_id)
                        found = True
                        break

            if not found:
                # если не нашли, то извлекаем id названия области и создаем новую область с текущим годом
                area_name_id = find_element_by_name(area_names, area_name).id
                area = Area(year=year, area_name_id=area_name_id)

            current_subject = None

            for p211_spo_data in area_data["p211"]:

                for subject in subjects:
                    if subject.area_id == area.id and subject.name == p211_spo_data['name']:
                        current_subject = subject

                if current_subject is None:
                    current_subject = Subject(code=p211_spo_data['code'], name=p211_spo_data['name'])
                    area.subjects.append(current_subject)

                current_p211_spo = P211_SPO()
                current_p211_spo.str_number = p211_spo_data['str_number']
                current_p211_spo.budget_amount = p211_spo_data['budget_amount']
                current_p211_spo.contract_amount = p211_spo_data['contract_amount']
                current_p211_spo.total_accepted = p211_spo_data['total_accepted']
                current_p211_spo.disabled_accepted = p211_spo_data['disabled_accepted']
                current_p211_spo.basic_level_amount = p211_spo_data['basic_level_amount']
                current_p211_spo.advanced_level = p211_spo_data['advanced_level']
                current_p211_spo.total_fed_amount = p211_spo_data['total_fed_amount']
                current_p211_spo.disabled_fed_amount = p211_spo_data['disabled_fed_amount']
                current_p211_spo.total_subject_amount = p211_spo_data['total_subject_amount']
                current_p211_spo.disabled_subject_amount = p211_spo_data['disabled_subject_amount']
                current_subject.P211_SPO.append(current_p211_spo)

            for p2121_spo_data in area_data["p2121"]:

                for subject in subjects:
                    if subject.area_id == area.id and subject.name == p2121_spo_data['name']:
                        current_subject = subject

                if current_subject is None:
                    current_subject = Subject(code=p2121_spo_data['code'], name=p2121_spo_data['name'])
                    area.subjects.append(current_subject)

                current_p2121_spo = P2121_SPO()
                current_p2121_spo.str_number = p2121_spo_data['str_number']

                current_subject.P2121_SPO.append(current_p2121_spo)

            for p2124_spo_data in area_data["p2124"]:

                for subject in subjects:
                    if subject.area_id == area.id and subject.name == p2124_spo_data['name']:
                        current_subject = subject

                if current_subject is None:
                    current_subject = Subject(code="", name=p2124_spo_data['name'])
                    area.subjects.append(current_subject)

                current_p2124_spo = P2124_SPO()
                current_p2124_spo.total_accepted = p2124_spo_data['total_accepted']
                current_p2124_spo.disabled_accepted = p2124_spo_data['disabled_accepted']
                current_p2124_spo.basic_level_amount = p2124_spo_data['basic_level_amount']
                current_p2124_spo.advanced_level = p2124_spo_data['advanced_level']
                current_p2124_spo.total_fed_amount = p2124_spo_data['total_fed_amount']
                current_p2124_spo.disabled_fed_amount = p2124_spo_data['disabled_fed_amount']
                current_p2124_spo.total_subject_amount = p2124_spo_data['total_subject_amount']
                current_p2124_spo.disabled_subject_amount = p2124_spo_data['disabled_subject_amount']
                current_p2124_spo.local_budget_amount = p2124_spo_data['local_budget_amount']
                current_p2124_spo.contract_amount = p2124_spo_data['contract_amount']
                current_p2124_spo.women_amount = p2124_spo_data['women_amount']
                current_p2124_spo.targeted_education = p2124_spo_data['targeted_education']
                current_subject.P2124_SPO.append(current_p2124_spo)

            for p2141_spo_data in area_data["p2141"]:

                for subject in subjects:
                    if subject.area_id == area.id and subject.name == p2141_spo_data['name']:
                        current_subject = subject

                if current_subject is None:
                    current_subject = Subject(code=p2141_spo_data['code'], name=p2141_spo_data['name'])
                    area.subjects.append(current_subject)

                current_p2141_spo = P2141_SPO()
                current_p2141_spo.str_number = p2141_spo_data['str_number']
                current_p2141_spo.serial_number = p2141_spo_data['serial_number']
                current_p2141_spo.total_amount = p2141_spo_data['total_amount']
                current_p2141_spo.total_fed_amount = p2141_spo_data['total_fed_amount']
                current_p2141_spo.total_subject_amount = p2141_spo_data['total_subject_amount']
                current_p2141_spo.local_budget_amount = p2141_spo_data['local_budget_amount']
                current_p2141_spo.legal_representative_amount = p2141_spo_data['legal_representative_amount']
                current_p2141_spo.individual_amount = p2141_spo_data['individual_amount']
                current_p2141_spo.legal_entity_amount = p2141_spo_data['legal_entity_amount']

                current_subject.P2141_SPO.append(current_p2141_spo)

            for p2142_spo_data in area_data["p2142"]:

                for subject in subjects:
                    if subject.area_id == area.id and subject.name == p2142_spo_data['name']:
                        current_subject = subject

                if current_subject is None:
                    current_subject = Subject(code=p2142_spo_data['code'], name=p2142_spo_data['name'])
                    area.subjects.append(current_subject)

                current_p2142_spo = P2142_SPO()
                current_p2142_spo.str_number = p2142_spo_data['str_number']
                current_p2142_spo.serial_number = p2142_spo_data['serial_number']
                current_p2142_spo.women_amount = p2142_spo_data['women_amount']
                current_p2142_spo.accelerated_learning = p2142_spo_data['accelerated_learning']
                current_p2142_spo.total_disabled_amount = p2142_spo_data['total_disabled_amount']
                current_p2142_spo.disabled_amount = p2142_spo_data['disabled_amount']
                current_p2142_spo.disabled_children_amount = p2142_spo_data['disabled_children_amount']
                current_p2142_spo.excepted_disabled = p2142_spo_data['excepted_disabled']
                current_p2142_spo.excepted_disabled_children = p2142_spo_data['excepted_disabled_children']

                current_subject.P2142_SPO.append(current_p2142_spo)

        session.commit()


@app.route('/api/year/spo_upload', methods=['POST', 'GET'])
def read_json_old_spo():
    base_dir = "C:\\Users\\protuberanzen\\PycharmProjects\\collecting-data\\vpo\\shortOldSpo\\"

    for file in os.listdir(base_dir):
        print(file)
        json_path = os.path.join(base_dir, file)
        with open(json_path, encoding='utf8') as json_file:
            json_data = json.load(json_file)

        area_names = [area.name.upper() for area in session.query(AreaName).all()]
        # добавляем области
        for area in json_data['areas']:
            area_name = area['name'].upper()
            if area_name not in area_names:
                session.add(AreaName(name=area_name))
                area_names.append(area_name)

        # заносим изменения в базу данных
        session.commit()

        # извлекаем уже обновленные данные из бд
        area_names = session.query(AreaName).all()
        areas = session.query(Area).all()
        subjects = session.query(Subject).all()

        year = json_data['year']
        for area_data in json_data['areas']:
            area_name = area_data['name'].upper()
            print(area_name)
            area = None
            found = False

            # находим область по названию и году
            for с in areas:
                name = с.area_name.name
                if name == area_name:
                    if с.year == int(year):
                        area = с
                        found = True
                        break
                    else:
                        area_name_id = find_element_by_name(area_names, area_name).id
                        area = Area(year=year, area_name_id=area_name_id)
                        found = True
                        break

            if not found:
                # если не нашли, то извлекаем id названия области и создаем новую область с текущим годом
                area_name_id = find_element_by_name(area_names, area_name).id
                area = Area(year=year, area_name_id=area_name_id)

            current_subject = None

            country_codes = [country.code for country in session.query(Country).all()]
            for el in area_data["p27"]:
                country_code = el['country_code']
                if country_code not in country_codes:
                    session.add(Country(name=el['name'].upper(), code=country_code))
                    country_codes.append(country_code)

            session.commit()

            for p211_spo_data in area_data["p211"]:

                for subject in subjects:
                    if subject.area_id == area.id and subject.name == p211_spo_data['name']:
                        current_subject = subject

                if current_subject is None:
                    current_subject = Subject(code=p211_spo_data['code'], name=p211_spo_data['name'])

                current_old_p211_spo = OldP211_SPO()
                current_old_p211_spo.str_number = p211_spo_data['str_number']
                current_old_p211_spo.applications_submitted = p211_spo_data['applications_submitted']
                current_old_p211_spo.total_accepted = p211_spo_data['total_accepted']
                current_old_p211_spo.basic_level_amount = p211_spo_data['basic_level_amount']
                current_old_p211_spo.advanced_level = p211_spo_data['advanced_level']
                current_old_p211_spo.fed_accepted = p211_spo_data['fed_accepted']
                current_old_p211_spo.subject_budget_accepted = p211_spo_data['subject_budget_accepted']
                current_old_p211_spo.local_budget_accepted = p211_spo_data['local_budget_accepted']
                current_old_p211_spo.full_refund = p211_spo_data['full_refund']
                current_subject.old_P211_SPO.append(current_old_p211_spo)

            for p212_spo_data in area_data["p212"]:

                for subject in subjects:
                    if subject.area_id == area.id and subject.name == p212_spo_data['name']:
                        current_subject = subject

                if current_subject is None:
                    current_subject = Subject(code=p212_spo_data['code'], name=p212_spo_data['name'])

                current_p212_spo = OldP212_SPO()
                current_p212_spo.str_number = p212_spo_data['str_number']
                current_p212_spo.total_course_1 = p212_spo_data['total_course_1']
                current_p212_spo.budget_course_1 = p212_spo_data['budget_course_1']
                current_p212_spo.total_course_2 = p212_spo_data['total_course_2']
                current_p212_spo.budget_course_2 = p212_spo_data['total_course_2']
                current_p212_spo.total_course_3 = p212_spo_data['total_course_3']
                current_p212_spo.budget_course_3 = p212_spo_data['budget_course_3']
                current_p212_spo.total_course_4 = p212_spo_data['total_course_4']
                current_p212_spo.budget_course_4 = p212_spo_data['budget_course_4']
                current_p212_spo.total_course_5 = p212_spo_data['total_course_5']
                current_p212_spo.budget_course_5 = p212_spo_data['budget_course_5']
                current_p212_spo.total_course_6 = p212_spo_data['total_course_6']
                current_p212_spo.budget_course_6 = p212_spo_data['budget_course_6']

                current_subject.old_P212_SPO.append(current_p212_spo)

            for p2122_spo_data in area_data["p2122"]:

                for subject in subjects:
                    if subject.area_id == area.id and subject.name == p2122_spo_data['name']:
                        current_subject = subject

                if current_subject is None:
                    current_subject = Subject(code="", name=p2122_spo_data['name'])

                current_p2122_spo = OldP2122_SPO()
                current_p2122_spo.basic_graduated = p2122_spo_data['basic_graduated']
                current_p2122_spo.advanced_graduated = p2122_spo_data['advanced_graduated']
                current_p2122_spo.total_graduated = p2122_spo_data['total_graduated']
                current_subject.old_P2122_SPO.append(current_p2122_spo)

            countries = session.query(Country).all()

            for p27_spo_data in area_data["p27"]:

                current_p27_spo = OldP27_SPO()
                code = p27_spo_data["country_code"]
                for с in countries:
                    if с.code == code:
                        current_p27_spo.country_id = с.id
                        break

                current_p27_spo.str_number = p27_spo_data['str_number']
                current_p27_spo.country_code = p27_spo_data['country_code']
                current_p27_spo.total_accepted = p27_spo_data['total_accepted']
                current_p27_spo.fed_budget_accepted = p27_spo_data['fed_budget_accepted']
                current_p27_spo.subject_budget_accepted = p27_spo_data['subject_budget_accepted']
                current_p27_spo.full_refund_accepted = p27_spo_data['full_refund_accepted']
                current_p27_spo.total_amount = p27_spo_data['total_amount']
                current_p27_spo.fed_budget_amount = p27_spo_data['fed_budget_amount']
                current_p27_spo.subject_budget_amount = p27_spo_data['subject_budget_amount']
                current_p27_spo.full_refund_amount = p27_spo_data['full_refund_amount']
                current_p27_spo.total_graduated = p27_spo_data['total_graduated']
                current_p27_spo.fed_budget_graduated = p27_spo_data['fed_budget_graduated']
                current_p27_spo.subject_budget_graduated = p27_spo_data['subject_budget_graduated']
                current_p27_spo.full_refund_graduated = p27_spo_data['full_refund_graduated']

                area.old_P27_SPO.append(current_p27_spo)

            area.subjects.append(current_subject)
            session.add(area)

        session.commit()
    print("success!")

@app.route('/api/year/summary_upload', methods=['POST', 'GET'])
def new_year_summary():
    json_data = json.loads(request.files['json_data'].read())
    area_names = [area.name.upper() for area in session.query(AreaName).all()]
    country_codes = [country.code for country in session.query(Country).all()]
    # добавляем страны, которых до этого не было
    for area_data in json_data['areas']:
        bachelor_data = area_data['bachelor']
        spec_data = area_data['spec']
        magistracy_data = area_data['magistracy']

        for el in bachelor_data:
            country_code = el['code']
            if country_code not in country_codes:
                session.add(Country(name=el['country'].upper(), code=country_code))
                country_codes.append(country_code)

        for el in spec_data:
            country_code = el['code']
            if country_code not in country_codes:
                session.add(Country(name=el['country'].upper(), code=country_code))
                country_codes.append(country_code)

        for el in magistracy_data:
            country_code = el['code']
            if country_code not in country_codes:
                session.add(Country(name=el['country'].upper(), code=country_code))
                country_codes.append(country_code)

    # добавляем области
    for area in json_data['areas']:
        area_name = area['name'].upper()
        if area_name not in area_names:
            session.add(AreaName(name=area_name))
            area_names.append(area_name)
    # заносим изменения в базу данных
    session.commit()

    # извлекаем уже обновленные данные из бд
    area_names = session.query(AreaName).all()
    areas = session.query(Area).all()
    countries = session.query(Country).all()

    year = json_data['year']
    for area_data in json_data['areas']:
        area_name = area_data['name'].upper()
        print(area_name)
        area = None
        found = False

        # находим область по названию и году
        for с in areas:
            name = с.area_name.name
            if name == area_name:
                if с.year == int(year):
                    area = с
                    found = True
                    break
                else:
                    area_name_id = find_element_by_name(area_names, area_name).id
                    area = Area(year=year, area_name_id=area_name_id)
                    found = True
                    break

        if not found:
            # если не нашли, то извлекаем id названия области и создаем новую область с текущим годом
            area_name_id = find_element_by_name(area_names, area_name).id
            area = Area(year=year, area_name_id=area_name_id)

        data_subjects = area_data['subjects']
        data_bachelors = area_data['bachelor']
        data_masters = area_data['magistracy']
        data_specialists = area_data['spec']

        for data_subject in data_subjects:
            current_subject = Subject(code=data_subject['code'], name=data_subject['name'])
            current_p211 = P211()
            data_current_p211 = data_subject['p211']
            current_p211.budget_amount = data_current_p211['budget_amount']
            current_p211.contract_amount = data_current_p211['contract_amount']
            current_p211.total_fed_amount = data_current_p211['total_fed_amount']
            current_p211.gr_contract_amount = data_current_p211['gr_contract_amount']
            current_p211.women_amount = data_current_p211['women_amount']

            current_p2124 = P2124()
            data_current_p2124 = data_subject['p2124']
            current_p2124.contract_amount = data_current_p2124['contract_amount']
            current_p2124.total_fed_amount = data_current_p2124['total_fed_amount']
            current_p2124.women_amount = data_current_p2124['women_amount']

            current_p213 = P213()
            data_current_p213 = data_subject['p213']
            current_p213.total_grad_amount = data_current_p213['total_grad_amount']
            current_p213.magistracy_amount = data_current_p213['magistracy_amount']
            current_p213.total_fed_amount = data_current_p213['total_fed_amount']
            current_p213.contract_amount = data_current_p213['contract_amount']
            current_p213.women_amount = data_current_p213['women_amount']

            current_subject.P211 = [current_p211]
            current_subject.P2124 = [current_p2124]
            current_subject.P213 = [current_p213]

            area.subjects.append(current_subject)

        for data_bachelor in data_bachelors:
            current_bachelor = PostgraduateBachelor()
            code = data_bachelor['code']
            for с in countries:
                if с.code == code:
                    current_bachelor.country_id = с.id

            current_bachelor.row_number = data_bachelor['row_number']
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
            area.postgraduate_bachelors.append(current_bachelor)

        for data_master in data_masters:
            current_master = PostgraduateMaster()
            code = data_master['code']
            for c in countries:
                if c.code == code:
                    current_master.country_id = c.id
            current_master.row_number = data_master['row_number']
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
            area.postgraduate_masters.append(current_master)

        for data_specialist in data_specialists:
            current_specialist = PostgraduateSpecialty()
            code = data_specialist['code']
            for c in countries:
                if c.code == code:
                    current_specialist.country_id = c.id
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
            area.postgraduate_specialists.append(current_specialist)

        session.add(area)

    session.commit()

    return "ok"


@app.cli.command('initdbVPO')
def read_json_vpo():
    base_dir = "C:\\Users\\nikita\\Downloads\\"

    for file in os.listdir(base_dir):
        print(file)
        json_path = os.path.join(base_dir, file)
        with open(json_path, encoding='utf8') as json_file:
            json_data = json.load(json_file)

        area_names = [area.name.upper() for area in session.query(AreaName).all()]
        country_codes = [country.code for country in session.query(Country).all()]
        # добавляем страны, которых до этого не было
        for area_data in json_data['areas']:
            bachelor_data = area_data['bachelor']
            spec_data = area_data['spec']
            magistracy_data = area_data['magistracy']

            for el in bachelor_data:
                country_code = el['code']
                if country_code not in country_codes:
                    session.add(Country(name=el['country'].upper(), code=country_code))
                    country_codes.append(country_code)

            for el in spec_data:
                country_code = el['code']
                if country_code not in country_codes:
                    session.add(Country(name=el['country'].upper(), code=country_code))
                    country_codes.append(country_code)

            for el in magistracy_data:
                country_code = el['code']
                if country_code not in country_codes:
                    session.add(Country(name=el['country'].upper(), code=country_code))
                    country_codes.append(country_code)

        # добавляем области
        for area in json_data['areas']:
            area_name = area['name'].upper()
            if area_name not in area_names:
                session.add(AreaName(name=area_name))
                area_names.append(area_name)
        # заносим изменения в базу данных
        session.commit()

        # извлекаем уже обновленные данные из бд
        area_names = session.query(AreaName).all()
        areas = session.query(Area).all()
        countries = session.query(Country).all()

        year = json_data['year']
        for area in json_data['areas']:
            area_name = area['name'].upper()
            print(area_name)
            area = None
            found = False

            # находим область по названию и году
            for с in areas:
                name = с.area_name.name
                if name == area_name:
                    if с.year == int(year):
                        area = с
                        found = True
                        break
                    else:
                        area_name_id = find_element_by_name(area_names, area_name).id
                        area = Area(year=year, area_name_id=area_name_id)
                        found = True
                        break

            if not found:
                # если не нашли, то извлекаем id названия области и создаем новую область с текущим годом
                area_name_id = find_element_by_name(area_names, area_name).id
                area = Area(year=year, area_name_id=area_name_id)

            data_subjects = area_data['subjects']
            data_bachelors = area_data['bachelor']
            data_masters = area_data['magistracy']
            data_specialists = area_data['spec']

            for data_subject in data_subjects:
                current_subject = Subject(code=data_subject['code'], name=data_subject['name'])
                current_p211 = P211()
                data_current_p211 = data_subject['p211']
                current_p211.budget_amount = data_current_p211['budget_amount']
                current_p211.contract_amount = data_current_p211['contract_amount']
                current_p211.total_fed_amount = data_current_p211['total_fed_amount']
                current_p211.gr_contract_amount = data_current_p211['gr_contract_amount']
                current_p211.women_amount = data_current_p211['women_amount']

                current_p2124 = P2124()
                data_current_p2124 = data_subject['p2124']
                current_p2124.contract_amount = data_current_p2124['contract_amount']
                current_p2124.total_fed_amount = data_current_p2124['total_fed_amount']
                current_p2124.women_amount = data_current_p2124['women_amount']

                current_p213 = P213()
                data_current_p213 = data_subject['p213']
                current_p213.total_grad_amount = data_current_p213['total_grad_amount']
                current_p213.magistracy_amount = data_current_p213['magistracy_amount']
                current_p213.total_fed_amount = data_current_p213['total_fed_amount']
                current_p213.contract_amount = data_current_p213['contract_amount']
                current_p213.women_amount = data_current_p213['women_amount']

                current_subject.P211 = [current_p211]
                current_subject.P2124 = [current_p2124]
                current_subject.P213 = [current_p213]

                area.subjects.append(current_subject)

            for data_bachelor in data_bachelors:
                current_bachelor = PostgraduateBachelor()
                code = data_bachelor['code']
                for с in countries:
                    if с.code == code:
                        current_bachelor.country_id = с.id

                current_bachelor.row_number = data_bachelor['row_number']
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
                area.postgraduate_bachelors.append(current_bachelor)

            for data_master in data_masters:
                current_master = PostgraduateMaster()
                code = data_master['code']
                for c in countries:
                    if c.code == code:
                        current_master.country_id = c.id
                current_master.row_number = data_master['row_number']
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
                area.postgraduate_masters.append(current_master)

            for data_specialist in data_specialists:
                current_specialist = PostgraduateSpecialty()
                code = data_specialist['code']
                for c in countries:
                    if c.code == code:
                        current_specialist.country_id = c.id
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
                area.postgraduate_specialists.append(current_specialist)

            session.add(area)

        session.commit()

    return "ok"


@app.cli.command('initdbOLDVPO')
def read_json_old_vpo():
    base_dir = "C:\\Users\\protuberanzen\\PycharmProjects\\collecting-data\\vpo\\shortOld\\"

    for file in os.listdir(base_dir):
        print(file)
        json_path = os.path.join(base_dir, file)
        with open(json_path, encoding='utf8') as json_file:
            json_data = json.load(json_file)

        area_names = [area.name.upper() for area in session.query(AreaName).all()]
        country_codes = [country.code for country in session.query(Country).all()]
        # добавляем страны, которых до этого не было
        for area_data in json_data['areas']:
            old_p210 = area_data['old_p210']

            for el in old_p210:
                country_code = el['code']
                if country_code not in country_codes:
                    session.add(Country(name=el['country'].upper(), code=country_code))
                    country_codes.append(country_code)

        # добавляем области
        for area in json_data['areas']:
            area_name = area['name'].upper()
            if area_name not in area_names:
                session.add(AreaName(name=area_name))
                area_names.append(area_name)
        # заносим изменения в базу данных
        session.commit()

        # извлекаем уже обновленные данные из бд
        area_names = session.query(AreaName).all()
        areas = session.query(Area).all()
        countries = session.query(Country).all()

        year = json_data['year']
        for area_data in json_data['areas']:
            area_name = area_data['name'].upper()
            print(area_name)
            area = None
            found = False

            # находим область по названию и году
            for с in areas:
                name = с.area_name.name
                if name == area_name:
                    if с.year == int(year):
                        area = с
                        found = True
                        break
                    else:
                        area_name_id = find_element_by_name(area_names, area_name).id
                        area = Area(year=year, area_name_id=area_name_id)
                        found = True
                        break

            if not found:
                # если не нашли, то извлекаем id названия области и создаем новую область с текущим годом
                area_name_id = find_element_by_name(area_names, area_name).id
                area = Area(year=year, area_name_id=area_name_id)

            print(area)
            data_subjects = area_data['subjects']

            for data_subject in data_subjects:
                current_subject = Subject(code=data_subject['code'], name=data_subject['name'])
                current_p211 = OldP211()
                data_current_p211 = data_subject['old_p211']
                current_p211.total_amount = data_current_p211['total_amount']
                current_p211.contract_amount = data_current_p211['contract_amount']
                current_p211.total_fed_amount = data_current_p211['total_fed_amount']

                current_p212 = OldP212()
                data_current_p212 = data_subject['old_p212']
                current_p212.total_fed_amount = data_current_p212['total_fed_amount']
                current_p212.contract_amount = data_current_p212['contract_amount']

                current_p212p = OldP212P()
                data_current_p212p = data_subject['old_p212P']
                current_p212p.total_fed_amount = data_current_p212p['total_fed_amount']
                current_p212p.contract_amount = data_current_p212p['contract_amount']
                current_p212p.women_amount = data_current_p212p['women_amount']

                current_subject.OldP211 = [current_p211]
                current_subject.OldP212 = [current_p212]
                current_subject.OldP212P = [current_p212p]

                area.subjects.append(current_subject)

            data_p25 = area_data['old_p25']

            for p25_row in data_p25:
                p25 = OldP25()
                p25.name = p25_row['name']
                p25.amount = p25_row['amount']
                area.old_P25.append(p25)

            data_p210 = area_data['old_p210']

            for p210_row in data_p210:
                p210 = OldP210()
                p210.row_number = int(p210_row['row_number'])
                p210.accepted_students_amount = p210_row['accepted_students_amount']
                p210.a_fed_budget = p210_row['a_fed_budget']
                p210.a_rf_budget = p210_row['a_rf_budget']
                p210.total_students_amount = p210_row['total_students_amount']
                p210.t_fed_budget = p210_row['t_fed_budget']
                p210.t_rf_budget = p210_row['t_rf_budget']
                p210.grad_students_amount = p210_row['grad_students_amount']
                p210.g_fed_budget = p210_row['g_fed_budget']
                p210.g_rf_budget = p210_row['g_rf_budget']
                area.old_P210.append(p210)

            session.add(area)

        session.commit()

    return "ok"


def find_element_by_name(array, target):
    for el in array:
        if el.name == target:
            return array[array.index(el)]
    return -1


if __name__ == '__main__':
    app.debug = True
    app.run()
