# -*- coding: utf-8 -*-
# @Time    : 2020/8/21 18:07
# @Author  : DUN
# @FileName: main2.py
# @Software: PyCharm
# @Blog    ：
from xlrd import open_workbook
from gensim import corpora, models, similarities
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer
from re import compile, sub
from itertools import groupby
import pandas as pd
import os

stemmer = LancasterStemmer()
wnl = WordNetLemmatizer()


def load_data():
    """读取excel"""
    worksheet = open_workbook('data.xlsx')
    sheet_names = worksheet.sheet_names()
    sheet = worksheet.sheet_by_name(sheet_names[0])
    rows = sheet.nrows  # 获取行数
    cols = sheet.ncols  # 获取列数，尽管没用到
    all_content = []
    i = 1
    while i < rows:
        cell = sheet.cell_value(i, 1)  # 取第二列数据
        try:
            all_content.append(cell)
        except ValueError as e:
            pass
        i += 1
    return all_content


def load_data_v2(key, value):
    """读取excel的特定行"""
    choose_index = pd.DataFrame(pd.read_excel("para_group.xlsx"))
    result = choose_index.loc[choose_index[key] == value]
    paragraph = pd.DataFrame(pd.read_excel("data.xlsx"))

    all_content = []
    for index, row in result.iterrows():
        choose_para = paragraph.loc[paragraph["file_name"] == row["file_name"]]
        all_content.append(choose_para.loc[:, "env_cov_para"].values[0])
    return all_content


def get_wordnet_pos(tag):
    if tag.startswith("J"):
        return wordnet.ADJ
    elif tag.startswith("V"):
        return wordnet.VERB
    elif tag.startswith("N"):
        return wordnet.NOUN
    elif tag.startswith("R"):
        return wordnet.ADV
    else:
        return None


def tokenize(documents):
    # 删词规则
    r0 = "[\d]+"
    r1 = "--+"
    r2 = "\(([i]{1,3}|(v[i]{1,4})|[\d]|[A-Za-z]{1})\)"
    r3 = "\n"
    # r4 = "\\【.*?】+|\\《.*?》+|\\#.*?#+|[.!/_,$&%^*()<>+""''``?@|:;~{}#]+|[——！\\\，。=？、：“”‘’￥……（）《》【】]"
    r4 = """[.!/_,$&%^*()<>+""''``?@|:;~{}#]+|[“”‘’]|(-[-]+)"""

    # 停用词
    stop = set(stopwords.words('english'))
    stop2 = set("shall could thereof hereof would likely without within upon may under except".split())
    # 不重要的名词+动词+形容词+副词
    with open("unimportant.txt", "r") as fr:
        lines = fr.read()
        unimportant = lines.split(" ")
        unimportant = set(unimportant)

    doc_words = []
    for doc in documents:
        sents = sent_tokenize(doc)
        word = []
        for sent in sents:
            # 正则过滤
            sent = sub(r0, '', sent)
            sent = sub(r1, '', sent)
            sent = sub(r2, '', sent)
            sent = sub(r3, ' ', sent)
            sent = sub(r4, '', sent)

            # 词形还原
            tagged_sent = pos_tag(word_tokenize(sent))  # 单词在句子中的词性
            groups = groupby(tagged_sent, key=lambda x: x[1])  # Group by tags
            names = [[w for w, _ in words] for tag, words in groups if tag == "NNP"]
            if names:
                name_set = set()
                name_list = []
                for nn in names:
                    if len(nn) >= 2 and "ETC" not in set(nn) and "Etc" not in set(nn):
                        for n in nn:
                            name_set.add(n)
                        name = " ".join(nn)
                        name_list.append(name)
                    # else:
                    #     name_set.add(nn[0])
                    #     name_list.append(nn[0])
                word.extend(name_list)

                lemmas_sent = []  # 非专有名词的单词按照词性还原（n-单复数还原，v-时态还原，a-比较级还原）
                for tag in tagged_sent:
                    if tag[0] not in name_set:
                        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
                        lemmas_sent.append(wnl.lemmatize(tag[0].lower(), pos=wordnet_pos))

                filter_sent = [w.lower() for w in lemmas_sent if
                               w.lower() not in stop and w.lower() not in stop2 and w.lower() not in unimportant and w.lower() not in name_set]  # 删除停用词和不重要词汇
            else:
                lemmas_sent = []  # 单词按照词性还原（n-单复数还原，v-时态还原，a-比较级还原）
                for tag in tagged_sent:
                    wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
                    lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos))
                filter_sent = [w.lower() for w in lemmas_sent if
                               w.lower() not in stop and w.lower() not in stop2 and w.lower() not in unimportant]

            word.extend(filter_sent)
        doc_words.append(word)
    return doc_words


def topic_of_document(doc, num_topics):
    maxx = doc[0][1]
    max_index = 0
    for i in range(num_topics):
        if doc[i][1] > maxx:
            maxx = doc[i][1]
            max_index = i
    return max_index


def bag_of_words(texts):
    """
    :param texts:
    :return:

    通过 gensim.corpora.dictionary.Dictionary
    分配了一个唯一的整型id给所有在语料库中出现过的词. 通过扫描整个文本，收集词汇数与相应的统计

    假设n个文档共有w个不重复词，则每一个文档都将用w维向量表示，以体现不同文档的特征
    """
    dictionary = corpora.Dictionary(texts)
    return dictionary


key = "icode300"
list_of_values = pd.DataFrame(pd.read_excel("para_group.xlsx"))[key]
a = [int(x) for x in list_of_values if not pd.isnull(x)]
set_of_values = set(a)
set_of_values = list(set_of_values)
for value in set_of_values:
    documents = load_data_v2(key, value)
    doc_words = tokenize(documents)
    dictionary = bag_of_words(doc_words)
    corpus = [dictionary.doc2bow(text) for text in doc_words]
    tfidf_model = models.TfidfModel(corpus)  # 建立TF-IDF模型
    corpus_tfidf = tfidf_model[corpus]
    num_topics = 3
    lda = models.LdaModel(corpus=corpus_tfidf, id2word=dictionary, num_topics=num_topics)

    root = "./log/20200823/{key}={value}/".format(key=key, value=value)
    if not os.path.exists(root):
        os.makedirs(root)
    # 展示每一个主题下权重最大的n个单词
    topic_list = lda.print_topics(num_words=15)
    print("{num_topics}个主题的单词分布为：".format(num_topics=num_topics))
    for topic in topic_list:
        print(topic)
        with open(root + "log.txt", "a", encoding='utf-8') as f:
            f.write("topic{i}, words:{list}".format(i=str(topic[0]), list=topic[1]))
            f.write("\n")

    # 文本分类存储
    for i in range(len(corpus_tfidf)):
        topic = topic_of_document(lda[corpus_tfidf[i]], num_topics)
        with open(root + "topic{i}.txt".format(i=topic), "a", encoding='utf-8') as f:
            words = doc_words[i]
            for wi in range(len(words)):
                f.write(words[wi] + ",")
        # print("document {index} topic {topic}".format(index=i, topic=topic))

    # lda模型评分
    goodcm = models.CoherenceModel(model=lda, corpus=corpus_tfidf,
                                   dictionary=dictionary, coherence='u_mass')
    print(goodcm.get_coherence())
    with open(root + "log.txt", "a", encoding='utf-8') as f:
        f.write(str(goodcm.get_coherence()))
        f.write("\n")