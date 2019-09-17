import unittest
from camelot.core import Table, Cell
from parser import \
    remove_num_prefix, \
    income_by_category, \
    row_is_empty, \
    category_for_row, \
    process_row, \
    process_table, \
    table_is_first_page_element, \
    merge_multi_page_table_data

class TestParser(unittest.TestCase):

    def test_remove_num_prefix_empty(self):
        actual = remove_num_prefix('1.')
        expected = ''
        self.assertEqual(actual, expected)

    def test_remove_num_prefix_space(self):
        actual = remove_num_prefix('1. ')
        expected = ''
        self.assertEqual(actual, expected)

    def test_remove_num_prefix_with_text(self):
        actual = remove_num_prefix('1. Mitglied des Vorstands ABC AG')
        expected = 'Mitglied des Vorstands ABC AG'
        self.assertEqual(actual, expected)

    def test_remove_num_prefix_multiple_spaces(self):
        actual = remove_num_prefix('1.    Mitglied des Vorstands ABC AG')
        expected = 'Mitglied des Vorstands ABC AG'
        self.assertEqual(actual, expected)

    def test_remove_num_prefix_multiple_nums(self):
        actual = remove_num_prefix('1. Mitglied im 1. Karnevalsverein e.V.')
        expected = 'Mitglied im 1. Karnevalsverein e.V.'
        self.assertEqual(actual, expected)

    def test_income_by_category_probono(self):
        self.assertEqual(income_by_category(0), [0, 0])

    def test_income_by_category_1(self):
        self.assertEqual(income_by_category(1), [1, 499])

    def test_income_by_category_2(self):
        self.assertEqual(income_by_category(2), [500, 1000])

    def test_income_by_category_3(self):
        self.assertEqual(income_by_category(3), [1001, 5000])

    def test_income_by_category_4(self):
        self.assertEqual(income_by_category(4), [5001, 10000])

    def test_income_by_category_5_lowest(self):
        self.assertEqual(income_by_category(5, 10000), [10001, 14999])

    def test_income_by_category_5(self):
        self.assertEqual(income_by_category(5, 20000), [15000, 24999])

    def test_row_is_empty_empty(self):
        row = ['1.']
        self.assertEqual(row_is_empty(row), True)

    def test_row_is_empty_not_empty(self):
        row = ['1. Mitglied des Vorstands ABC AG']
        self.assertEqual(row_is_empty(row), False)

    def test_category_for_row_with_probono_lowest(self):
        # +-------------+-----------------+---+---+---+---+---+
        # | Description | nicht verguetet | 1 | 2 | 3 | 4 | 5 |
        # +-------------+-----------------+---+---+---+---+---+
        # | Lorem Ipsum |        X        |   |   |   |   |   |
        # +-------------+-----------------+---+---+---+---+---+
        row = ['1. Lorem Ipsum', 'X', '', '', '', '', '']
        self.assertEqual(category_for_row(row), [0, None])

    def test_category_for_row_with_probono_highest(self):
        # +-------------+-----------------+---+---+---+---+---+
        # | Description | nicht verguetet | 1 | 2 | 3 | 4 | 5 |
        # +-------------+-----------------+---+---+---+---+---+
        # | Lorem Ipsum |                 |   |   |   |   | X |
        # +-------------+-----------------+---+---+---+---+---+
        row = ['1. Lorem Ipsum', '', '', '', '', '', '30000']
        self.assertEqual(category_for_row(row), [5, 30000])

    def test_category_for_row_lowest(self):
        # +-------------+---+---+---+---+---+
        # | Description | 1 | 2 | 3 | 4 | 5 |
        # +-------------+---+---+---+---+---+
        # | Lorem Ipsum | X |   |   |   |   |
        # +-------------+---+---+---+---+---+
        row = ['1. Lorem Ipsum', 'X', '', '', '', '']
        self.assertEqual(category_for_row(row), [1, None])

    def test_category_for_row_highest(self):
        # +-------------+---+---+---+---+---+
        # | Description | 1 | 2 | 3 | 4 | 5 |
        # +-------------+---+---+---+---+---+
        # | Lorem Ipsum |   |   |   |   | X |
        # +-------------+---+---+---+---+---+
        row = ['1. Lorem Ipsum', '', '', '', '', '30000']
        self.assertEqual(category_for_row(row), [5, 30000])

    def test_process_row(self):
        actual = process_row(['1. Lorem Ipsum', 'X', '', '', '', '', ''])
        expected = {'description': 'Lorem Ipsum', 'income': [0, 0]}
        self.assertDictEqual(actual, expected)

    def test_process_table(self):
        actual = process_table([
            ['1. Lorem Ipsum', 'X', '', '', '', '', ''],
            ['2. Dolor Sit Amet', '', '', '', '', '', '30000'],
            ['3. ', '', '', '', '', '', ''],
        ])

        expected = [
            {'description': 'Lorem Ipsum', 'income': [0, 0]},
            {'description': 'Dolor Sit Amet', 'income': [25000, 34999]},
        ]

        self.assertItemsEqual(actual, expected)

    def test_table_starts_at_top_true(self):
        #               x1 x2       y1   y2
        table = Table([(0, 100)], [(749, 1000)])
        table.cells[0][0] = Cell(0, 749, 100, 1000)

        self.assertTrue(table_is_first_page_element(table))

    def test_table_starts_at_top_false(self):
        table = Table([(0, 100)], [(1000, 1500)])
        table.cells[0][0] = Cell(0, 1000, 100, 1500)

        self.assertFalse(table_is_first_page_element(table))

    def test_merge_multi_page_table_data_successive_tables(self):
        first_part = Table([(0, 100)], [(1000, 1500)])
        first_cell = Cell(0, 1000, 100, 1500)
        first_cell.text = 'FIRST CELL'
        first_part.cells[0][0] = first_cell

        second_part = Table([(0, 100)], [(749, 1000)])
        second_cell = Cell(0, 749, 100, 1000)
        second_cell.text = 'SECOND CELL'
        second_part.cells[0][0] = second_cell

        actual = merge_multi_page_table_data([first_part, second_part])
        expected = [[['FIRST CELL'], ['SECOND CELL']]] # single 2:1 table
        self.assertListEqual(actual, expected)

    def test_merge_multi_page_table_data_different_tables(self):
        first_part = Table([(0, 100)], [(1000, 1500)])
        first_cell = Cell(0, 1000, 100, 1500)
        first_cell.text = 'FIRST CELL'
        first_part.cells[0][0] = first_cell

        second_part = Table([(0, 100)], [(1000, 1500)])
        second_cell = Cell(0, 1000, 100, 1500)
        second_cell.text = 'SECOND CELL'
        second_part.cells[0][0] = second_cell

        actual = merge_multi_page_table_data([first_part, second_part])
        expected = [[['FIRST CELL']], [['SECOND CELL']]] # two 1:1 tables
        self.assertListEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
