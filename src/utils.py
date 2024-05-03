import requests
import psycopg2
from contextlib import closing
import configparser


def get_data_from_hh(company_ids: list) -> dict:
    """
    Получает данные о вакансиях компаний по их идентификаторам с использованием API сайта HeadHunter.

    Для каждого идентификатора компании из списка company_ids функция отправляет HTTP-запрос к API HH (HeadHunter)
    и собирает информацию о вакансиях данной компании. Информация возвращается в виде словаря, где ключом является
    идентификатор компании, а значением - данные о вакансиях в формате JSON.

    :param company_ids: Список идентификаторов компаний для поиска вакансий.
    :return: Словарь, где ключ - идентификатор компании, значение - данные о вакансиях этой компании.
    """

    base_url = "https://api.hh.ru/"
    companies_data = {}

    for company_id in company_ids:
        params = {'employer_id': company_id}
        response = requests.get(f"{base_url}vacancies", params=params)
        companies_data[company_id] = response.json()

        company_name = requests.get(f"{base_url}employers/{company_id}")
        companies_data[company_id]['company_name'] = company_name.json()['name']

    return companies_data


def insert_companies_into_db(companies_ids):
    """

    :return:
    """

    config = configparser.ConfigParser()
    config.read("settings.ini")

    with closing(psycopg2.connect(
        host=config.get("Open_db", "host"),
        database=config.get("Open_db", "database"),
        user=config.get("Open_db", "user"),
        password=config.get("Open_db", "password")
    )) as conn:
        with conn.cursor() as cur:
            pass



def insert_vacancies_into_db(companies_data):
    """

    :param companies_data:
    :return:
    """

    config = configparser.ConfigParser()
    config.read("settings.ini")

    with closing(psycopg2.connect(
        host=config.get("Open_db", "host"),
        database=config.get("Open_db", "database"),
        user=config.get("Open_db", "user"),
        password=config.get("Open_db", "password")
    )) as conn:
        with conn.cursor() as cur:

            for company_id, data in companies_data.items():
                for item in data['items']:
                    cur.execute(
                        "INSERT INTO vacancies (vacancy_id, company_id, name, salary_min, salary_max, currency, url) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (vacancy_id) DO NOTHING",
                        (item['id'], company_id, item['name'], item['salary']['from'], item['salary']['to'],
                        item['salary']['currency'], item['alternate_url']))
