from src.service.search_pattern import search_images_keyword
from src.service.filters import filter_rows
from src.service.console_output import print_search_results
import os
from src.lib.Timer import timer

@timer
def search_e(query) : 
    """search cased query"""
    rows = search_images_keyword(query, 5)
    filtered = filter_rows(rows, query)
    print_search_results(filtered, images_dir=os.getenv("IMAGE_DIR"))

@timer
def search_i(query) : 
    """search uncased query"""
    rows = search_images_keyword(query.lower(), 5)
    filtered = filter_rows(rows, query, ignore_case=True)
    print_search_results(filtered, images_dir=os.getenv("IMAGE_DIR"))

@timer
def search_c(query: str) -> None:
    """count occurrences (matching images)"""
    rows = search_images_keyword(query, 500)
    filtered = filter_rows(rows, query)
    print(len(filtered))