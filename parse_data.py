# -*- coding: utf-8 -*-
import json

# pase_1
'''
读取名为 {num}_ner_train.json 和 {num}_ner_dev.json 的文件，其中 {num} 是从 1 到 6 的数字。
将训练集和开发集的数据合并为一个数据集。
将数据集中的每个样本转换为指定格式的字典，包括 id、data 和 label 三个字段。
将转换后的数据保存到名为 {num}_ner_train_data.json 的新文件中。
在代码的末尾，使用一个循环来遍历数字 1 到 6，并依次调用 parse_2 函数，以处理每个数字对应的数据集文件。
'''

def parse_2(num):
    with open("data/{}_ner.json".format(num), "r", encoding="utf-8") as f:
        aa = json.load(f)
    #with open("./dataset/{}_ner_dev.json".format(num), "r", encoding="utf-8") as f:
        #bb = json.load(f)
    #train_data = aa+bb
    train_data = aa
    aa_w = open("data/{}_ner_train_data.json".format(num), "w", encoding="utf-8")
    for i, one in enumerate(train_data):
        adta = {"id": 574714, "data": "", "label": []}
        if i == 0:
            print(one)
        adta["data"] = one.get("text")
        for p in one.get("entities"):
            adta["label"].append([p.get("start"), p.get("end"), p.get("type")])
        aa_w.write(json.dumps(adta, ensure_ascii=False) + "\n")

for i in range(1,7):
    parse_2(i)
