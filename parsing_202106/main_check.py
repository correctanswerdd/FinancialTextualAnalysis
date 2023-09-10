import os
import pandas as pd
from Document import Document

if __name__ == '__main__':
    filename = "19950324_10-K_edgar_data_55785_0000055785-95-000007_1.txt"
    year = 1995
    qtr = 1
    base = './{year}/QTR{index}/{filename}'.format(year=year, index=qtr, filename=filename)
    data = []

    with open(base, 'r', encoding="utf-8") as f:
        filecontent = f.read()
    d = Document(filecontent)
    d.find_item1()
    d.find_item2()
    d.find_item7()
    row = 65873, year, d.item1, d.item1_case, d.item1_reason, d.item1_len, d.item2, d.item2_case, d.item2_reason, d.item2_len, d.item7, d.item7_case, d.item7_reason, d.item7_len, "+".join(d.note), "=HYPERLINK(\"{path}\")".format(path=base)
    data.append(row)

    df = pd.DataFrame(data, columns=['cik', 'year', 'item1', 'item1 case', 'item1 reason', "item1 length", 'item2',
                                     'item2 case', 'item2 reason',
                                     'item2 length', 'item7', 'item7 case', 'item7 reason', 'item7 length', "note",
                                     'path'])
    df.to_csv(r'0722_test_output_{year}_{index}.csv'.format(year=year, index=qtr), index=False, header=True)
