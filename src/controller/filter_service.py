from model.filter import Filter


class FilterService:
    def __init__(self):
        pass

    def get_filter_name_from_str(self, filters_list: list[Filter], name: str) -> str:
        existing_names = {filter.name for filter in filters_list}
        original_name = name
        count = 1

        while name in existing_names:
            name = f"{original_name}_{count}"
            count += 1

        return name
