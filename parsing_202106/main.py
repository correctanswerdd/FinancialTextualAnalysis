import os
import pandas as pd
from Document import Document
from pathlib import Path


def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname


def searchCik(filebase_list, cik):
    for i in filebase_list:
        filename = i[12:]
        s = filename.split("_")
        if s[4] == cik:
            return i
    return ""


def main(year, qtr):
    filename = "wrds_link_hcik_gvkey.csv"
    df = pd.read_csv(filename)
    df["cik"] = df["cik"].astype(str)

    # year = 1995
    # qtr = 1
    base = './{year}/QTR{index}'.format(year=year, index=qtr)
    data = []

    output_base = "./files_{year}/QTR{index}".format(year=year, index=qtr)
    Path(output_base).mkdir(parents=True, exist_ok=True)

    for filebase in findAllFile(base):
        if "_10-K_" in filebase:
            filename = filebase[12:]
            s = filename.split("_")
            cik = s[4]
            if cik in df.cik.values:
                """
                1750 in df.cik => true
                "1750" in df.cik.values => true
                """
                print(filename)
                with open(filebase, 'r', encoding="utf-8") as f:
                    filecontent = f.read()
                d = Document(filecontent)

                d.find_item1()
                item1_path = "{output_base}/{name}_item1.txt".format(output_base=output_base, name=filename[:-4])
                with open(item1_path, "w") as f:
                    f.write(d.item1)

                d.find_item2()
                item2_path = "{output_base}/{name}_item2.txt".format(output_base=output_base, name=filename[:-4])
                with open(item2_path, "w") as f:
                    f.write(d.item2)

                d.find_item7()
                item7_path = "{output_base}/{name}_item7.txt".format(output_base=output_base, name=filename[:-4])
                with open(item7_path, "w") as f:
                    f.write(d.item7)

                row = cik, year, "=HYPERLINK(\"{path}\")".format(
                    path=item1_path), d.item1_case, d.item1_reason, d.item1_len, "=HYPERLINK(\"{path}\")".format(
                    path=item2_path), d.item2_case, d.item2_reason, d.item2_len, "=HYPERLINK(\"{path}\")".format(
                    path=item7_path), d.item7_case, d.item7_reason, d.item7_len, "=HYPERLINK(\"{path}\")".format(
                    path=filebase)
                data.append(row)

    df = pd.DataFrame(data, columns=['cik', 'year', 'item1', 'item1 case', 'item1 reason', "item1 length", 'item2',
                                     'item2 case', 'item2 reason',
                                     'item2 length', 'item7', 'item7 case', 'item7 reason', 'item7 length',
                                     'path'])
    df.to_csv(r'0728index_{year}_{index}.csv'.format(year=year, index=qtr), index=False, header=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    for year in range(2013, 2019):
        for qtr in range(1, 5):
            # print(year, qtr)
            main(year, qtr)
