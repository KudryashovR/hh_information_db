from pprint import pprint


from src.utils import get_data_from_hh


def main():
    emp_ids = [
        1942330, 49357, 78638, 2748, 1648566, 2180, 3529, 1942336, 196621, 4352
    ]

    pprint(get_data_from_hh(emp_ids))


if __name__ == "__main__":
    main()
