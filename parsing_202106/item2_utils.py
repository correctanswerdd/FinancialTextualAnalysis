import os
import re
import numpy as np
import pandas as pd


def reason_why_no_item2(filecontent):
    item_list = filecontent.lower().split("item")
    item_neighbours = [i[0:100] for i in item_list]

    for neighbour in item_neighbours:  # item+business的组合可能是item1的起始位置
        if "properties" in neighbour:
            return "wrong regular expression. raw text = {text}".format(text=neighbour)

    return "indeed no item2 in whole text"


def item2_find_table(filecontent):
    table_boundary = 40  # ps. boundary过大可能导致很小的item2被认为是table

    pattern_item2 = re.compile(r"item\s*2\.\s*[\s\S]*?item\s*3\.\s*", re.IGNORECASE)
    match = pattern_item2.search(filecontent)
    if match:
        start, end = match.span()
        text = filecontent[start: end]
        text = text.replace(".", " ")
        words = text.split()
        if len(words) > table_boundary:
            return False, -1
        else:
            return True, end

    return "", -1


def item2_find_table0(filecontent):
    table_boundary = 100
    lines = filecontent.split("\n")
    start_status = False
    n = -1000000
    pattern_start = re.compile(r"item\s*2\.*\s*\b", re.IGNORECASE)
    pattern_end = re.compile(r"item\s*3\.", re.IGNORECASE)
    text = []
    for line in lines:
        match_start = pattern_start.search(line)
        match_end = pattern_end.search(line)
        if match_start and not start_status:
            start_status = True
            n = 0
            text.append(line)
        if start_status:
            n += 1
            text.append(line)
        if match_end and start_status:
            text.append(line)
            match_end = pattern_end.search(filecontent)
            start, end = match_end.span()
            if n <= table_boundary:
                text = " ".join(text)
                words = text.split(" ")
                if len(words) >= 60:  # 虽然n很小，但是这一段可能是文本正文，而不是table
                    return False, -1
                else:
                    return True, end  # find table
            else:
                return False, -1

    return "", -1


def find_item2_longest(filecontent):
    pattern_item2 = re.compile(r"item\s*2\.\s*[\s\S]*item\s*3\.\s*", re.IGNORECASE)
    match = pattern_item2.search(filecontent)
    return match
