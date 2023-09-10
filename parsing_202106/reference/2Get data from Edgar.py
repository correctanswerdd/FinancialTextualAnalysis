import argparse
import requests
import json
import pandas as pd
from io import StringIO
import pickle
from concurrent.futures import ThreadPoolExecutor
import re
import os
import time

capital_letters = '|'.join(['credit agreement',
                            'loan agreement'
                            ])
capital_letters_html = '>[^<>]*({})[ \t]*</'.format(capital_letters)
sequence_term = '^<SEQUENCE>'
text_term = '^<TEXT>'
end_text_term = '^</TEXT>'
page_term = '^<PAGE>'
next_search_term = '^[ \t]*TABLE OF CONTENTS|<[^<]*>[  \t]*TABLE OF CONTENTS[ \t]*</.*?>'
next_search_term_02 = '^[ \t]*TABLE OF CONTENTS|<[^<>]*>[  \t]*TABLE OF CONTENTS[ \t]*</[^<>]*>'
sequence_term_pattern = re.compile(sequence_term)
text_term_pattern = re.compile(text_term)
end_text_term_pattern = re.compile(end_text_term)
capital_letters_pattern = re.compile(capital_letters, re.I)
next_search_term_pattern = re.compile(next_search_term)
next_search_term_pattern_02 = re.compile(next_search_term_02)
html = '<HTML[^<>]*>|<DIV[^<>]*'
html_re = re.compile(html, re.I)
capital_letters_html_pattern = re.compile(capital_letters_html, re.I)
page_term_pattern = re.compile(page_term)
FULL_INDEX_URL = 'https://www.sec.gov/Archives/edgar/full-index/'

CLOUD_URL = 'https://www.sec.gov/Archives/'
OUTPUT_DIR = '.'
MAX_RETRY = 12
MAX_WORKS = 1
FAIL_LIST = []


def search(row_data):
    find_list = []
    start_text = 0
    for index, row in enumerate(row_data):
        for group in find_list:
            group[1] += 1
        if sequence_term_pattern.search(row):
            find_list = []
        if text_term_pattern.search(row):
            start_text = index
        if capital_letters_pattern.search(row):
            find_list.append([index, 0])
        if next_search_term_pattern.search(row):
            for start_row, span in find_list:
                end_text = 0
                for l_, row_ in enumerate(row_data[index + 1:]):
                    if end_text_term_pattern.search(row_):
                        end_text = index + 1 + l_
                        break
                return start_text, end_text, start_row, span, row_data[start_text:end_text + 1]
    return None

def search_02(row_data):
    find_list = []
    page_list = []
    if html_re.search(' '.join(row_data[:100])):
        capital_letters_pattern_ = capital_letters_html_pattern
    else:
        capital_letters_pattern_ = capital_letters_pattern
    for index, row in enumerate(row_data):
        for group in find_list:
            group[1] += 1
        if sequence_term_pattern.search(row):
            find_list = []
        if page_term_pattern.search(row):
            page_list.append(index)
        if capital_letters_pattern_.search(row):
            find_list.append([(index, capital_letters_pattern_.search(row).span()[-1]), 0])
        elif capital_letters_pattern.search(row):
            find_list.append([(index, capital_letters_pattern.search(row).span()[-1]), 0])
        if next_search_term_pattern_02.search(row):
            if len(find_list) > 0:
                (start_row, offset), span = find_list[-1]
                if html_re.search(' '.join(row_data[:300])):
                    if index == start_row:
                        if offset < next_search_term_pattern_02.search(row).span()[0]:
                            return row_data[1:-1], 1
                        else:
                            break
                    else:
                        return row_data[1:-1], 1
                else:
                    start_page = 0
                    for i, p in enumerate(page_list):
                        if p <= start_row:
                            start_page = p
                        else:
                            break
                    if start_page - start_row > 10:
                        return row_data[start_page + 1:-1], 0
                    else:
                        return row_data[max(start_row - 3, 0):-1], 0
            else:
                break
    return None, -1


def search_by_year(year_href):
    print('=' * 100)
    print('{0} start'.format(year_href))
    year_index_url = '{0}{1}{2}'.format(FULL_INDEX_URL, year_href, 'index.json')
    year_response = requests.get(year_index_url)
    year_json = json.loads(year_response.text)
    for qtr in year_json['directory']['item']:
        print('-' * 50)
        print('{0} {1} start'.format(year_href, qtr['href']))
        #if qtr['href'] != 'QTR4/':
        #    continue
        # 3.2 Get quarter json
        qtr_href = qtr['href']
        qtr_index_url = '{0}{1}{2}{3}'.format(FULL_INDEX_URL, year_href, qtr_href, 'index.json')
        download_flag = False
        qtr_json = None
        for c in range(MAX_RETRY):
            try:
                qtr_response = requests.get(qtr_index_url)
                qtr_json = json.loads(qtr_response.text)
                download_flag = True
                break
            except:
                print('{0} cat not download,retry {1}'.format(qtr_index_url, c))
                time.sleep(10)
        if download_flag:
            # 3.3 Filter and get master.idx
            master = list(filter(lambda x: x['name'] == 'master.idx', qtr_json['directory']['item']))[0]['href']
            master_url = '{0}{1}{2}{3}'.format(FULL_INDEX_URL, year_href, qtr_href, master)
            master_response = requests.get(master_url)
            master_text = master_response.text
            # 3.4 Convert master.idx to DataFrame
            master_file = StringIO(master_text)
            master_df = pd.read_csv(master_file, sep='|', skiprows=lambda x: x in list(range(8)) + [10])
            # 3.5 Filter by 10Q,10K,8K Form Type
            master_df_slt = master_df.loc[master_df['Form Type'].isin(["10-K", "10-K/A", "10-K405", "10-K405/A",
                                                                       "10-KSB", "10-KSB/A", "10-KT", "10-KT/A",
                                                                       "10KSB", "10KSB/A", "10KSB40", "10KSB40/A",
                                                                       "10KT405", "10KT405/A", "10-Q", "10-Q/A",
                                                                       "10-Q405", "10-Q405/A", "10-QSB", "10-QSB/A",
                                                                       "10-QT", "10-QT/A", "10QSB", "10QSB/A",
                                                                       "10QSB40", "10QSB40/A", "10QT405", "10QT405/A",
                                                                       "8-K", "8K", "8-K/A", "8K/A"])]
            executor = ThreadPoolExecutor(max_workers=MAX_WORKS)

            def fetch_data(fn):
                raw_file_txt = None
                file_n = '{0}{1}'.format(CLOUD_URL, fn)
                for c in range(MAX_RETRY):
                    try:
                        raw_file_response = requests.get(file_n)
                        raw_file_txt = raw_file_response.text
                        break
                    except:
                        print('{0}{1} cat not download,retry {2}'.format(CLOUD_URL, fn, c))
                        time.sleep(10)
                return file_n, raw_file_txt

            all_c = len(master_df_slt)
            print('size of files : {}'.format(all_c))
            drop_c = 0
            fail_c = 0
            true_c = 0
            for i, (f, data) in enumerate(executor.map(fetch_data, master_df_slt['Filename'].tolist())):
                if data is None:
                    fail_c += 1
                    yield f, -2
                else:
                    row_data = data.split('\n')
                    result_ = search(row_data)
                    if result_ is not None:
                        row_data = result_[-1]
                        result_02, signal = search_02(row_data)
                        if result_02 is not None:
                            true_c += 1
                            yield (f, result_02), signal
                        else:
                            drop_c += 1
                    else:
                        drop_c += 1
                p = (drop_c + fail_c + true_c) / all_c * 100
                print('{} {} -- all:{}\tdrop:{}\tfail:{}\tsave:{} --- {:.4f}%'.format(year_href, qtr['href'], all_c,
                                                                                      drop_c, fail_c, true_c, p))
            print('{0} {1} completed'.format(year_href, qtr['href']))
        else:
            yield (qtr_index_url, -1)
            print('{0} {1} failed'.format(year_href, qtr['href']))
        print('-' * 50)
    print('{0} completed'.format(year_href))
    print('=' * 100)


def save_text(pre, suf, row):
    url, data = row
    with open(os.path.join(pre, url[-24:-3] + suf), 'w') as f:
        for l in data:
            f.write(l)
            f.write('\n')


def save_plk(ob, file):
    with open(file, 'wb') as f:
        pickle.dump(ob, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_path",
        type=str,
        default="./result",
        help="output path"
    )
    parser.add_argument(
        "--max_works",
        type=int,
        default=2,
        help="max works"
    )
    parser.add_argument(
        "--start_year",
        type=int,
        default=2019,
        help="start year"
    )
    parser.add_argument(
        "--end_year",
        type=int,
        default=2019,
        help="end year"
    )
    FLAGS, _ = parser.parse_known_args()
    OUTPUT_DIR = FLAGS.output_path
    MAX_WORKS = FLAGS.max_works
    start_year = FLAGS.start_year
    end_year = FLAGS.end_year
    response = requests.get('{0}{1}'.format(FULL_INDEX_URL, 'index.json'))
    json_data = json.loads(response.text)
    item_list = json_data['directory']['item']
    item_list = filter(lambda item_: item_['type'] == 'dir' and start_year <= int(item_['name']) <= end_year, item_list)
    for item in item_list:
        path = os.path.join(OUTPUT_DIR, str(item['name']), 'result')
        if not os.path.exists(path):
            os.makedirs(path)
        result = []
        fail = []
        for r, flag in search_by_year(item['href']):
            result.append(r)
            if flag == 0:
                save_text(path, 'txt', r)
            elif flag == 1:
                save_text(path, 'html', r)
            else:
                fail.append(r)
        save_plk(result, os.path.join(OUTPUT_DIR, str(item['name']), 'result-{}.plk'.format(item['name'])))
        save_plk(fail, os.path.join(OUTPUT_DIR, str(item['name']), 'fail-{}.plk'.format(item['name'])))
