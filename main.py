from pprint import pprint

from src.utils import get_data_from_hh, insert_vacancies_into_db, insert_companies_into_db, clear_tables, create_tables
from src.dbmanager import DBManager


def main():
    emp_ids = [
        1942330, 49357, 78638, 2748, 1648566, 2180, 3529, 1942336, 196621, 4352
    ]

    received_data = get_data_from_hh(emp_ids)
    create_tables()
    clear_tables()

    for company_id, company_data in received_data.items():
        insert_companies_into_db(company_id, company_data)
        insert_vacancies_into_db(company_id, company_data.get("items"))

    vacancies_db = DBManager()

    while True:
        user_mode = input("Функции:\n1. Получить список всех компаний и количество вакансий у каждой компании.\n"
                          "2. Получить список всех вакансий с указанием названия компании, названия вакансии "
                          "и зарплаты и ссылки на вакансию.\n3. Получить среднюю зарплату по вакансиям.\n4. Получить "
                          "список всех вакансий, у которых зарплата выше средней по всем вакансиям.\n5. получает "
                          "список всех вакансий, в названии которых содержатся переданные в метод слова, например "
                          "python.\nЛюбой символ для завершения.\n")

        match user_mode:
            case '1':
                pprint(vacancies_db.get_companies_and_vacancies_count())
            case '2':
                pprint(vacancies_db.get_all_vacancies())
            case '3':
                pprint(vacancies_db.get_avg_salary())
            case '4':
                pprint(vacancies_db.get_vacancies_with_higher_salary())
            case '5':
                pprint(vacancies_db.get_vacancies_with_keyword(input("Введите строку поиска: ")))
            case _:
                print("Завершение работы")

                break

    vacancies_db.release_db()


if __name__ == "__main__":
    main()
