from src.utils import get_data_from_hh, insert_vacancies_into_db, insert_companies_into_db,clear_tables, create_tables


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


if __name__ == "__main__":
    main()
