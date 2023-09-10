import pandas as pd
from item1_utils import item1_find_table, find_item1_longest, reason_why_no_item1
from item2_utils import item2_find_table, find_item2_longest, reason_why_no_item2
from item7_utils import item7_find_table, find_item7_longest, reason_why_no_item7
from utils import check_item, cut_item, filter_item


class Document:
    def __init__(self, file_content):
        self.file_content = file_content
        self.item1 = ""
        self.item1_case = None
        self.item1_reason = None
        self.item1_len = None
        self.item2 = ""
        self.item2_case = None
        self.item2_reason = ""
        self.item2_len = None
        self.item7 = ""
        self.item7_case = None
        self.item7_reason = None
        self.item7_len = None

    def find_item1(self):
        file_content = self.file_content
        flag_find_table, table_end_index = item1_find_table(file_content)

        if flag_find_table:  # find the table
            file_content = self.file_content[table_end_index:]
            match_of_possible_item1 = find_item1_longest(file_content)
            if match_of_possible_item1:
                start, end = match_of_possible_item1.span()
                # CASE 1 OR 2
                text = file_content[start: end]
                self.item1_case, self.item1, self.item1_reason = filter_item(text, 3, "properties")
                self.item1_len = len(self.item1)
            else:
                # CASE 4
                self.item1_case = 4
                self.item1_reason = reason_why_no_item1(file_content)
        elif flag_find_table == "":
            # CASE 3
            self.item1_case = 3
            self.item1_reason = reason_why_no_item1(file_content)
        else:
            match_of_possible_item1 = find_item1_longest(file_content)
            if match_of_possible_item1:
                start, end = match_of_possible_item1.span()
                # CASE 1 OR 2
                text = file_content[start: end]
                self.item1_case, self.item1, self.item1_reason = filter_item(text, 3, "properties")
                self.item1_len = len(self.item1)
            else:
                # CASE 3
                self.item1_case = 3
                self.item1_reason = reason_why_no_item1(file_content)

    def find_item2(self):
        file_content = self.file_content
        flag_find_table, table_end_index = item2_find_table(file_content)

        if flag_find_table:  # find the table
            file_content = self.file_content[table_end_index:]
            match_of_possible_item2 = find_item2_longest(file_content)
            if match_of_possible_item2:
                start, end = match_of_possible_item2.span()
                # CASE 1 OR 2
                text = file_content[start: end]
                self.item2_case, self.item2, self.item2_reason = filter_item(text, 4, "proceedings")
                self.item2_len = len(self.item2)
            else:
                # CASE 4
                self.item2_case = 4
                self.item2_reason = reason_why_no_item2(file_content)
        elif flag_find_table == "":
            # CASE 3
            self.item2_case = 3
            self.item2_reason = reason_why_no_item2(file_content)
        else:
            match_of_possible_item2 = find_item2_longest(file_content)
            if match_of_possible_item2:
                start, end = match_of_possible_item2.span()
                # CASE 1 OR 2
                text = file_content[start: end]
                self.item2_case, self.item2, self.item2_reason = filter_item(text, 4, "proceedings")
                self.item2_len = len(self.item2)
            else:
                # CASE 3
                self.item2_case = 3
                self.item2_reason = reason_why_no_item2(file_content)

    def find_item7(self):
        file_content = self.file_content
        flag_find_table, table_end_index = item7_find_table(file_content)

        if flag_find_table:  # find the table
            file_content = self.file_content[table_end_index:]
            match_of_possible_item7 = find_item7_longest(file_content)
            if match_of_possible_item7:
                start, end = match_of_possible_item7.span()
                # CASE 1 OR 2
                text = file_content[start: end]
                self.item7_case, self.item7, self.item7_reason = filter_item(text, 9, "financial")
                self.item7_len = len(self.item7)
            else:
                # CASE 4
                self.item7_case = 4
                self.item7_reason = reason_why_no_item7(file_content)
        elif flag_find_table == "":
            # CASE 3
            self.item7_case = 3
            self.item7_reason = reason_why_no_item7(file_content)
        else:
            match_of_possible_item7 = find_item7_longest(file_content)
            if match_of_possible_item7:
                start, end = match_of_possible_item7.span()
                # CASE 1 OR 2
                text = file_content[start: end]
                self.item7_case, self.item7, self.item7_reason = filter_item(text, 9, "financial")
                self.item7_len = len(self.item7)
            else:
                # CASE 3
                self.item7_case = 3
                self.item7_reason = reason_why_no_item7(file_content)
