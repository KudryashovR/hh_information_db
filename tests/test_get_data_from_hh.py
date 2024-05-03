import pytest
from unittest.mock import patch


from src.utils import get_data_from_hh


def test_get_data_from_hh_empty():
    """
    Тест с пустым списком идентификаторов. Проверяет, что возвращается пустой словарь.
    """

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {}

        assert get_data_from_hh([]) == {}


def test_get_data_from_hh_single_id():
    """
    Тест с одним идентификатором. Проверяет корректность данных для одной компании.
    """

    company_id = 123
    expected_data = {'items': [
            {'id': '1', 'title': 'Developer'}
        ]}

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = expected_data
        result = get_data_from_hh([company_id])

        assert result == {company_id: expected_data}


def test_get_data_from_hh_failed_request():
    """
    Тест на проверку ситуации с сетевой ошибкой или ошибкой доступа к API.
    """

    company_ids = [123]

    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Network Failure")

        with pytest.raises(Exception) as exc_info:
            get_data_from_hh(company_ids)

        assert str(exc_info.value) == "Network Failure"
