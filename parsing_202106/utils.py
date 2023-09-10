import os
import re
import numpy as np
import pandas as pd

state_names = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
               "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
               "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
               "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
               "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
               "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
               "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
               "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

pattern00 = re.compile(r"item\s*1\.\s*\b", re.IGNORECASE)
pattern0 = re.compile(r"item\s*1a\.\s*\b", re.IGNORECASE)
pattern1 = re.compile(r"item\s*1b\.\s*\b", re.IGNORECASE)
pattern2 = re.compile(r"item\s*2\.\s*\b", re.IGNORECASE)
pattern3 = re.compile(r"item\s*3\.\s*\b", re.IGNORECASE)
pattern4 = re.compile(r"item\s*4\.\s*\b", re.IGNORECASE)
pattern5 = re.compile(r"item\s*5\.\s*\b", re.IGNORECASE)
pattern6 = re.compile(r"item\s*6\.\s*\b", re.IGNORECASE)
pattern7 = re.compile(r"item\s*7\.\s*\b", re.IGNORECASE)
pattern8 = re.compile(r"item\s*8\.\s*\b", re.IGNORECASE)
pattern9 = re.compile(r"item\s*9\.\s*\b", re.IGNORECASE)
patternList = [pattern00, pattern0, pattern1, pattern2, pattern3, pattern4, pattern5, pattern6, pattern7, pattern8,
               pattern9]


def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname


def check_item(local):
    # global case
    count_additional_match = 0
    neighbours = []

    for pattern in patternList:
        match = pattern.search(local)
        if match:  # wrong longest match
            start, end = match.span()
            count_additional_match += 1
            neighbour = local[end - 100: end + 100]  # if end < 100, neighbour=""
            neighbours.append(neighbour)

    if count_additional_match >= 3:
        return 1, "NEIGHBOUR" + ">>>>\n".join(neighbours)
    else:
        return 2, "correct local item"


def filter_item(local, pattern_idx, flag_word):
    # local本身已经干净了
    case, nbs = check_item(local)
    if case == 2:
        return 2, local, ""

    # 如果local可疑，则继续：
    pattern = patternList[pattern_idx]  # item尾部定位词
    f = re.finditer(pattern, local)
    end = len(local)
    for i in reversed(list(f)):
        start, end = i.span()
        if flag_word in local[end: end + 100].lower():
            case, nbs = check_item(local[: end])
            if case == 2:
                return 2, local[: end], ""
    # local遍历每一个尾部定位词后，依然找不到合法item->说明local本身已经干净了
    return 1, local[: end], nbs


def cut_item(local, item_idx):
    """
    excel一个格子最多存32000字符
    :param local:
    :return:
    """
    if len(local) >= 32000:
        return "cuted local item{idx}".format(idx=item_idx), local[:31000]
    return "no cut", local


def state_count(item, item_index, cik, year):
    for state in state_names:
        ct = item.count(state)
        if ct > 0:
            row = cik, year, item_index, state, ct
            yield row
