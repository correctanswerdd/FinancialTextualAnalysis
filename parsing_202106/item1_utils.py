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

def reason_why_no_item1(filecontent):
    item_list = filecontent.lower().split("item")
    item_neighbours = [i[0:100] for i in item_list]

    for neighbour in item_neighbours:  # item+business的组合可能是item1的起始位置
        if "business" in neighbour:
            return "wrong regular expression. raw text = {text}".format(text=neighbour)

    return "indeed no item1 in whole text"


def item1_find_table_0(filecontent):
    # global case
    table_boundary = 500
    # table阈值设置过小，会导致大的table被判断为"正文"。
    # 最后check_item时，这一段正文当中，由于存在连续的item1item2item3...，会被划分为case1。

    pattern_item1 = re.compile(r"item\s*1\.\s*[\s\S]*?item\s*1a\.\s*", re.IGNORECASE)
    match = pattern_item1.search(filecontent)
    if match:
        start, end = match.span()
        if end - start > table_boundary:  # matched text is not table(default: no table contained in this matched text, though there may exist table in there)
            return False, -1
        else:
            return True, end

    # print("     search item1->item1b")
    pattern_item1 = re.compile(r"item\s*1\.\s*[\s\S]*?item\s*1b\.\s*", re.IGNORECASE)
    match = pattern_item1.search(filecontent)
    if match:
        start, end = match.span()
        if end - start > table_boundary:  # matched text is not table
            return False, -1
        else:
            return True, end

    # print("     search item1->item2")
    pattern_item1 = re.compile(r"item\s*1\.\s*[\s\S]*?item\s*2\.\s*", re.IGNORECASE)
    match = pattern_item1.search(filecontent)
    if match:
        start, end = match.span()
        if end - start > table_boundary:  # matched text is not table
            return False, -1
        else:
            return True, end

    # print("     No item1 from whole text during TABLE CHECK!!!")
    # case = 3
    return "", -1


def item1_find_table(filecontent):
    table_boundary = 100
    lines = filecontent.split("\n")
    start_status = False
    n = -1000000
    pattern_start = re.compile(r"item\s*1\.*\s*\b", re.IGNORECASE)
    pattern_end = re.compile(r"item\s*1a\.|item\s*1b\.|item\s*2\.", re.IGNORECASE)
    for line in lines:
        match_start = pattern_start.search(line)
        match_end = pattern_end.search(line)
        if match_start and not start_status:
            start_status = True
            n = 0
        if start_status:
            n += 1
        if match_end and start_status:
            match_end = pattern_end.search(filecontent)
            start, end = match_end.span()
            if n <= table_boundary:
                return True, end  # find table
            else:
                return False, -1  # 找到的不是table

    return "", -1


def find_item1_longest(filecontent):
    pattern_item1 = re.compile(r"item\s*1\.\s*[\s\S]*item\s*1a\.\s*", re.IGNORECASE)
    match = pattern_item1.search(filecontent)
    if match:
        return match
    else:
        pattern_item1 = re.compile(r"item\s*1\.\s*[\s\S]*item\s*1b\.\s*", re.IGNORECASE)
        match = pattern_item1.search(filecontent)
        if match:
            return match
        else:
            pattern_item1 = re.compile(r"item\s*1\.\s*[\s\S]*item\s*2\.\s*", re.IGNORECASE)
            match = pattern_item1.search(filecontent)
            return match
