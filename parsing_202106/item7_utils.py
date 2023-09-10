import os
import re
import numpy as np
import pandas as pd


# path = "E:/0613textualanalysis"
# os.chdir(path)
# case = -1


# case = 1: there may be OTHER ITEMS in this local item.
# case = 2: correct local item
# case = 3: No item1 from whole text
# case = 4: No item1 after the table


def reason_why_no_item7(filecontent):
    item_list = filecontent.lower().split("item")
    item_neighbours = [i[0:100] for i in item_list]

    for neighbour in item_neighbours:  # item+business的组合可能是item1的起始位置
        if "discussion" in neighbour:
            return "wrong regular expression. raw text = {text}".format(text=neighbour)

    return "indeed no item7 in whole text"


def item7_find_table(filecontent):
    table_boundary = 40  # ps. boundary过大可能导致很小的item7被认为是table

    pattern_item7 = re.compile(r"item\s*7\.\s*[\s\S]*?item\s*8\.\s*", re.IGNORECASE)
    match = pattern_item7.search(filecontent)
    if match:
        start, end = match.span()
        text = filecontent[start: end]
        text = text.replace(".", " ")
        words = text.split()
        if len(words) > table_boundary:  # matched text is not table(default: no table contained in this matched text, though there may exist table in there)
            return False, -1
        else:
            return True, end

    return "", -1


def item7_find_table0(filecontent):
    table_boundary = 100
    lines = filecontent.split("\n")
    start_status = False
    n = -1000000
    pattern_start = re.compile(r"item\s*7\.*\s*\b", re.IGNORECASE)
    pattern_end = re.compile(r"item\s*8\.", re.IGNORECASE)
    for line in lines:
        match_start = pattern_start.search(line)
        match_end = pattern_end.search(line)
        if match_start and not start_status:
            start_status = True
            n = 1
        if start_status:
            n += 1
        if match_end and start_status:
            match_end = pattern_end.search(filecontent)
            start, end = match_end.span()
            if n <= table_boundary:
                return True, end  # find table
            else:
                return False, -1

    return "", -1


def find_item7_longest(filecontent):
    pattern_item7 = re.compile(r"item\s*7\.\s*[\s\S]*item\s*8\.\s*", re.IGNORECASE)
    match = pattern_item7.search(filecontent)
    return match
