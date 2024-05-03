import requests
import psycopg2
import configparser
import re


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

        company_data = requests.get(f"{base_url}employers/{company_id}")
        companies_data[company_id]['company_name'] = company_data.json()['name']
        companies_data[company_id]['company_description'] = remove_html_tags(company_data.json()['description'])

    return companies_data


def remove_html_tags(text: str) -> str:
    """
    Удаляет HTML теги из заданной строки.

    :param text: Строка, из которой необходимо удалить HTML теги.
    :return: Строка с удаленными HTML тегами.
    """

    clean_text = re.sub('<.*?>', '', text)

    return clean_text


def create_tables() -> None:
    """
    Создание таблиц в базе данных.

    Функция подключается к базе данных, настройки которой указаны в файле 'settings.ini'.
    Выполняется создание таблиц 'companies' и 'vacancies', если они ещё не существуют.

    Таблица 'companies' содержит следующие поля:
        - id: серийный уникальный идентификатор записи (основной ключ),
        - company_id: уникальный идентификатор компании,
        - company_name: название компании (до 255 символов),
        - description: текстовое описание компании.

    Таблица 'vacancies' включает в себя поля:
        - id: серийный уникальный идентификатор записи (основной ключ),
        - vacancy_id: уникальный идентификатор вакансии,
        - company_id: идентификатор компании, которой принадлежит вакансия,
        - vacancy_name: название вакансии (до 255 символов),
        - salary_min: минимальный уровень зарплаты,
        - salary_max: максимальный уровень зарплаты,
        - currency: валюта зарплаты (до 50 символов),
        - url: URL вакансии,
        - FOREIGN KEY (company_id) REFERENCES companies(company_id): внешний ключ, связывающий с таблицей 'companies'.

    Функция не принимает аргументов и не возвращает значений. Использует контекстное управление подключением и курсором,
    чтобы гарантировать закрытие соединений даже при возникновении ошибок.
    :return:
    """

    config = configparser.ConfigParser()
    config.read("settings.ini")

    with psycopg2.connect(
            host=config.get("Open_db", "host"),
            database=config.get("Open_db", "database"),
            user=config.get("Open_db", "user"),
            password=config.get("Open_db", "password")
    ) as conn:
        with conn.cursor() as cur:
            query = ("CREATE TABLE IF NOT EXISTS companies (id SERIAL PRIMARY KEY, company_id INTEGER UNIQUE, "
                     "company_name VARCHAR(255), description TEXT);")
            cur.execute(query)

            query = ("CREATE TABLE IF NOT EXISTS vacancies (id SERIAL PRIMARY KEY, vacancy_id INTEGER UNIQUE, "
                     "company_id INTEGER, vacancy_name VARCHAR(255), salary_min INTEGER, salary_max INTEGER, "
                     "currency VARCHAR(50), url VARCHAR(255), FOREIGN KEY (company_id) "
                     "REFERENCES companies(company_id));")
            cur.execute(query)

    conn.close()


def clear_tables() -> None:
    """
    Очистка таблиц базы данных.

    Функция осуществляет подключение к базе данных, указанной в файле 'settings.ini', и выполняет очистку таблиц
    'vacancies' и 'companies'. Таблица 'vacancies' очищается с перезапуском идентификаторов, тогда как удаление записей
    из 'companies' происходит с удалением всех зависимых записей (каскадное удаление).

    Функция не принимает аргументов и не возвращает значений. Использует контекстное управление подключением и курсором
    для гарантии закрытия соединения и курсора даже в случае возникновения ошибок.
    """

    config = configparser.ConfigParser()
    config.read("settings.ini")

    with psycopg2.connect(
            host=config.get("Open_db", "host"),
            database=config.get("Open_db", "database"),
            user=config.get("Open_db", "user"),
            password=config.get("Open_db", "password")
    ) as conn:
        with conn.cursor() as cur:
            query = "TRUNCATE vacancies RESTART IDENTITY;"
            cur.execute(query)

            query = "DELETE FROM companies CASCADE;"
            cur.execute(query)

    conn.close()


def insert_companies_into_db(company_id: str, company_data: dict) -> None:
    """
    Вставка данных о компании в таблицу 'companies'.

    Функция подключается к базе данных PostgreSQL, используя параметры из 'settings.ini', и вставляет информацию
    о компании в таблицу 'companies'.

    Аргументы:
        company_id (str): Уникальный идентификатор компании.
        company_data (dict): Словарь с данными о компании, содержащий ключи:
            - 'company_name': название компании (строка),
            - 'company_description': описание компании (строка).

    Функция не возвращает значений, но вносит изменения в базу данных, добавляя новую запись в таблицу. Используется
    контекстное управление подключением и курсором для гарантии закрытия соединения, даже если в процессе выполнения
    произойдет ошибка.

    Пример использования:
        insert_companies_into_db('123', {'company_name': 'XYZ Corp', 'company_description': 'Технологичная компания
        XYZ.'})
    """

    config = configparser.ConfigParser()
    config.read("settings.ini")

    with psycopg2.connect(
        host=config.get("Open_db", "host"),
        database=config.get("Open_db", "database"),
        user=config.get("Open_db", "user"),
        password=config.get("Open_db", "password")
    ) as conn:
        with conn.cursor() as cur:
            query = (f"INSERT INTO companies (company_id, company_name, description) VALUES ({company_id}, "
                     f"\'{company_data.get('company_name')}\', \'{company_data.get('company_description')}\');")
            cur.execute(query)

    conn.close()


def insert_vacancies_into_db(company_id, company_data):
    """
    Вставка данных о вакансиях компании в таблицу 'vacancies' базы данных.

    Функция подключается к базе данных PostgreSQL, используя параметры из файла 'settings.ini', и вставляет информацию
    о вакансиях в таблицу. Данные каждой вакансии из списка добавляются в таблицу.

    Параметры:
        company_id: Идентификатор компании, к которой относятся вакансии.
        company_data: Список словарей, каждый из которых представляет вакансию с ключами:
            - 'id': идентификатор вакансии,
            - 'name': название вакансии,
            - 'salary': словарь с информацией о заработной плате, содержащий:
                - 'from': минимальный размер заработной платы,
                - 'to': максимальный размер заработной платы,
                - 'currency': валюта заработной платы,
            - 'url': URL-адрес страницы вакансии.

    Каждая вакансия добавляется в базу с проверкой и адаптацией неуказанных или неполных данных о зарплате. Функция
    не возвращает значений, но выполняет вставку данных в базу данных.

    Пример использования:
        vacancies_data = [
            {"id": "1", "name": "Разработчик Python", "salary": {"from": 100000, "to": 150000, "currency": "руб."},
             "url": "example.com/vacancy1"},
            {"id": "2", "name": "Менеджер проектов", "salary": {"from": 80000, "to": 120000, "currency": "руб."},
             "url": "example.com/vacancy2"}
        ]
        insert_vacancies_into_db('123', vacancies_data)
    """

    config = configparser.ConfigParser()
    config.read("settings.ini")

    with psycopg2.connect(
        host=config.get("Open_db", "host"),
        database=config.get("Open_db", "database"),
        user=config.get("Open_db", "user"),
        password=config.get("Open_db", "password")
    ) as conn:
        with conn.cursor() as cur:
            for item in company_data:
                salary = item.get("salary")

                if salary is None:
                    salary = {"currency": "Не задано", "from": 0, "to": 0}

                salary_min = salary.get("from")

                if salary_min is None:
                    salary_min = 0

                salary_max = salary.get("to")

                if salary_max is None:
                    salary_max = 0

                query = (f"INSERT INTO vacancies (vacancy_id, company_id, vacancy_name, salary_min, salary_max, "
                         f"currency, url) VALUES ({item.get("id")}, {company_id}, \'{item.get("name")}\', "
                         f"{salary_min}, {salary_max}, \'{salary.get("currency", "Не задано")}\', "
                         f"\'{item.get("url")}\');")
                cur.execute(query)

    conn.close()
