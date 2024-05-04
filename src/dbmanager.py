from decimal import Decimal

import psycopg2
import configparser


class DBManager:
    """
    Класс для управления взаимодействием с базой данных PostgreSQL через psycopg2. Предоставляет методы для получения
    информации о компаниях, вакансиях, а также для выполнения специфических запросов.
    """

    __slots__= ['conn']

    def __init__(self) -> None:
        """
        Инициализирует подключение к базе данных с помощью учетных данных указанных в settings.ini.
        """

        config = configparser.ConfigParser()
        config.read("settings.ini")

        self.conn = psycopg2.connect(
            host=config.get("Open_db", "host"),
            database=config.get("Open_db", "database"),
            user=config.get("Open_db", "user"),
            password=config.get("Open_db", "password")
        )

    def get_companies_and_vacancies_count(self) -> list[tuple]:
        """
        Подсчитывает количество вакансий для каждой компании.

        Returns:
            list of tuple: Список кортежей, где каждый кортеж содержит название компании и количество вакансий.
        """

        cur = self.conn.cursor()

        query = ("SELECT companies.company_name, COUNT(vacancies.id) FROM companies JOIN vacancies "
                 "ON companies.company_id = vacancies.company_id GROUP BY companies.company_name")
        cur.execute(query)

        results = cur.fetchall()
        cur.close()

        return results

    def get_all_vacancies(self) -> list[tuple]:
        """
        Получает список всех вакансий с их основной информацией.

        Returns:
            list of tuple: Список кортежей, содержащий информацию о каждой вакансии.
        """

        cur = self.conn.cursor()

        query = ("SELECT companies.company_name, vacancies.vacancy_name, vacancies.salary_min, vacancies.salary_max, "
                 "vacancies.currency, vacancies.url FROM vacancies JOIN companies "
                 "ON vacancies.company_id = companies.company_id")
        cur.execute(query)

        vacancies = cur.fetchall()
        cur.close()

        return vacancies

    def get_avg_salary(self) -> 'Decimal':
        """
        Рассчитывает среднюю заработную плату по всем вакансиям.

        Returns:
            Decimal: Средняя заработная плата.
        """

        cur = self.conn.cursor()

        query = ("SELECT AVG((salary_min + salary_max) / 2) FROM vacancies WHERE salary_min IS NOT NULL "
                 "AND salary_max IS NOT NULL")
        cur.execute(query)
        avg_salary = cur.fetchone()[0]
        cur.close()

        return avg_salary

    def get_vacancies_with_higher_salary(self) -> list[tuple]:
        """
        Получает список вакансий с зарплатой выше средней.

        Returns:
            list of tuple: Список кортежей, содержащий название вакансии и среднюю зарплату.
        """

        avg_salary = self.get_avg_salary()
        cur = self.conn.cursor()

        query = (f"SELECT vacancy_name, (salary_min + salary_max) / 2 as average_salary FROM vacancies "
                 f"WHERE (salary_min + salary_max) / 2 > {avg_salary}")
        cur.execute(query)

        results = cur.fetchall()
        cur.close()

        return results

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """
        Ищет вакансии, содержащие заданное ключевое слово в названии.

        Параметры:
            keyword (str): Ключевое слово для поиска в названиях вакансий.

        Returns:
            list of tuple: Список кортежей, содержащий название вакансии и URL.
        """

        cur = self.conn.cursor()

        query = f"SELECT vacancy_name, url FROM vacancies WHERE vacancy_name ILIKE \'%{keyword}%\'"
        cur.execute(query)

        results = cur.fetchall()
        cur.close()

        return results

    def release_db(self) -> None:
        """
        Закрывает подключение к базе данных.
        """

        self.conn.close()
