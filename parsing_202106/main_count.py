import os
from utils import state_count
import pandas as pd


def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname


def main(year, qtr):
    # year = 1995
    # qtr = 1
    base = "./files_{year}/QTR{index}".format(year=year, index=qtr)
    data = []

    for filebase in findAllFile(base):
        filename = filebase[18:]
        print(filename)

        s = filename.split("_")
        cik = s[4]
        item_index = s[7][-5]

        with open(filebase, 'r', encoding="utf-8") as f:
            filecontent = f.read()

        for row in state_count(filecontent, item_index, cik, year):  # count states in ITEM1 and record it
            data.append(row)

    df = pd.DataFrame(data, columns=['cik', 'year', 'index', 'state', 'count'])
    df.to_csv(r'0728count_{year}_{index}.csv'.format(year=year, index=qtr), index=False, header=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    for year in range(1995, 2019):
        for qtr in range(1, 5):
            # print(year, qtr)
            main(year, qtr)
