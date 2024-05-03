import requests


def get_data_from_hh(company_ids: list) -> dict:
    """
    Получает данные о вакансиях компаний по их идентификаторам с использованием API сайта HeadHunter.

    Для каждого идентификатора компании из списка company_ids функция отправляет HTTP-запрос к API HH (HeadHunter)
    и собирает информацию о вакансиях данной компании. Информация возвращается в виде словаря, где ключом является
    идентификатор компании, а значением - данные о вакансиях в формате JSON.

    :param company_ids: Список идентификаторов компаний для поиска вакансий.
    :return: Словарь, где ключ - идентификатор компании, значение - данные о вакансиях этой компании.
    """

    base_url = "https://api.hh.ru/vacancies"
    companies_data = {}

    for company_id in company_ids:
        params = {'employer_id': company_id}
        response = requests.get(base_url, params=params)
        companies_data[company_id] = response.json()

    return companies_data
