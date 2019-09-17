import camelot
import re
import copy

PAGE_TOP = 749

def remove_num_prefix(string):
    return re.sub(r'^\d+\.\s*', '', string)

def income_by_category(category, nearest=10000):
    category_income_mapping = {
        0: [0, 0],
        1: [1, 499],
        2: [500, 1000],
        3: [1001, 5000],
        4: [5001, 10000],
    }

    if(category == 5 and nearest == 10000):
        return [10001, 14999]

    if(category == 5 and nearest > 10000):
        lower = nearest - 5000
        upper = nearest + 4999
        return [lower, upper]

    if(0 <= category <= 4):
        return category_income_mapping[category]

def row_is_empty(row):
    return remove_num_prefix(row[0]) == ''

def row_is_in_body(row):
    return re.match(r'^\d+\.', row[0])

def category_for_row(row):
    if(len(row) == 6):
        lowest = 1
    if(len(row) == 7):
        lowest = 0

    row = row[1:]

    index = next(i for i, v in enumerate(row) if v)
    category = lowest + index

    if(category == 5):
        return [category, int(row[index])]

    return [category, None]

def process_row(row):
    category = category_for_row(row)

    return {
        'description': remove_num_prefix(row[0]),
        'income': income_by_category(category[0], category[1]),
    }

def process_table(table):
    body_rows = [x for x in table if row_is_in_body(x)]
    non_empty_rows = [x for x in body_rows if not row_is_empty(x)]
    return [process_row(x) for x in non_empty_rows]

def table_is_first_page_element(table):
    return int(table.cells[0][0].y1) == PAGE_TOP

def merge_multi_page_table_data(tables):
    """
    Camelot doesn't recognize tables spanning multiple pages as
    separate tables per page. Merges multiple successive tables.
    """

    data = [x.data for x in tables]
    to_remove = []

    for index, table in enumerate(tables):
        if(index == 0):
            continue

        prev = tables[index - 1]

        if(table_is_first_page_element(table)):
            data[index - 1] = data[index - 1] + data[index]
            to_remove.append(index)

    return [x for index, x in enumerate(data) if index not in to_remove]

def parse(file):
    tables = camelot.read_pdf(file, pages='all')
    tables = merge_multi_page_table_data(tables)

    return {
        'article_42a': process_table(tables[0]),
        'article_42c': process_table(tables[2]),
        'article_42d': process_table(tables[3]),
        'article_42e': process_table(tables[4]),
        # 'article_42f': process_table(tables[5]),
    }
