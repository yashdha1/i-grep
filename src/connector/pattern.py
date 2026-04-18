from src.service.search_pattern import search_images_keyword
from src.service.filters import filter_rows
from src.service.console_output import print_search_results
from src.lib.Timer import timer

@timer
def search_e(query, limit: int = 5) : 
    """search cased query"""
    rows = search_images_keyword(query, 500)
    filtered = filter_rows(rows, query)
    print_search_results(filtered, pattern=query, limit=limit)

@timer
def search_i(query, limit: int = 5) : 
    """search uncased query"""
    rows = search_images_keyword(query.lower(), 500)
    filtered = filter_rows(rows, query, ignore_case=True)
    print_search_results(filtered, pattern=query, ignore_case=True, limit=limit)

@timer
def search_c(query: str) -> None:
    """count frequencies"""
    rows = search_images_keyword(query, 500)
    filtered = filter_rows(rows, query)
    print(len(filtered))