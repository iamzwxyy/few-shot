# -*- coding: utf-8 -*-
import os
import time
import argparse
import json
from decimal import Decimal
import numpy as np

from util.utils import set_seed, convert_ext_examples, convert_cls_examples, logger


def do_convert():
    set_seed(args.seed)

    tic_time = time.time()
    if not os.path.exists(args.doccano_file):
        raise ValueError("Please input the correct path of doccano file.")

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    if len(args.splits) != 0 and len(args.splits) != 3:
        raise ValueError("Only []/ len(splits)==3 accepted for splits.")

    def _check_sum(splits):
        return Decimal(str(splits[0])) + Decimal(str(splits[1])) + Decimal(
            str(splits[2])) == Decimal("1")

    if len(args.splits) == 3 and not _check_sum(args.splits):
        raise ValueError(
            "Please set correct splits, sum of elements in splits should be equal to 1."
        )

    with open(args.doccano_file, "r", encoding="utf-8") as f:
        raw_examples = f.readlines()

    def _create_ext_examples(examples,
                             negative_ratio=0,
                             shuffle=False,
                             is_train=True):
        entities, relations = convert_ext_examples(
            examples, negative_ratio, is_train=is_train)
        examples = entities + relations
        if shuffle:
            indexes = np.random.permutation(len(examples))
            examples = [examples[i] for i in indexes]
        return examples

    def _create_cls_examples(examples, prompt_prefix, options, shuffle=False):
        examples = convert_cls_examples(examples, prompt_prefix, options)
        if shuffle:
            indexes = np.random.permutation(len(examples))
            examples = [examples[i] for i in indexes]
        return examples

    def _save_examples(save_dir, file_name, examples):
        count = 0
        save_path = os.path.join(save_dir, file_name)
        if not examples:
            logger.info("Skip saving %d examples to %s." % (0, save_path))
            return
        with open(save_path, "w", encoding="utf-8") as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
                count += 1
        logger.info("Save %d examples to %s." % (count, save_path))

    if len(args.splits) == 0:
        if args.task_type == "ext":
            examples = _create_ext_examples(raw_examples, args.negative_ratio,
                                            args.is_shuffle)
        else:
            examples = _create_cls_examples(raw_examples, args.prompt_prefix,
                                            args.options, args.is_shuffle)
        _save_examples(args.save_dir, "train.txt", examples)
    else:
        if args.is_shuffle:
            indexes = np.random.permutation(len(raw_examples))
            raw_examples = [raw_examples[i] for i in indexes]

        i1, i2, _ = args.splits
        p1 = int(len(raw_examples) * i1)
        p2 = int(len(raw_examples) * (i1 + i2))

        if args.task_type == "ext":
            train_examples = _create_ext_examples(
                raw_examples[:p1], args.negative_ratio, args.is_shuffle)
            dev_examples = _create_ext_examples(
                raw_examples[p1:p2], -1, is_train=False)
            test_examples = _create_ext_examples(
                raw_examples[p2:], -1, is_train=False)
        else:
            train_examples = _create_cls_examples(
                raw_examples[:p1], args.prompt_prefix, args.options)
            dev_examples = _create_cls_examples(
                raw_examples[p1:p2], args.prompt_prefix, args.options)
            test_examples = _create_cls_examples(
                raw_examples[p2:], args.prompt_prefix, args.options)

        _save_examples(args.save_dir, args.save_train, train_examples)
        _save_examples(args.save_dir, "dev.txt", dev_examples)
        _save_examples(args.save_dir, "test1.txt", test_examples)

    logger.info('Finished! It takes %.2f seconds' % (time.time() - tic_time))


if __name__ == "__main__":
    # yapf: disable
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--doccano_file", default="./data/6_ner_train_data.json",
                        type=str, help="The doccano file exported from doccano platform.")
    parser.add_argument("-save_p", "--save_train", default="trains6.txt",
                        type=str, help="The doccano file exported from doccano platform.")
    parser.add_argument("-s", "--save_dir", default="data",
                        type=str, help="The path of data that you wanna save.")
    parser.add_argument("--negative_ratio", default=4, type=int,
                        help="Used only for the extraction task, the ratio of positive and negative samples, number of negtive samples = negative_ratio * number of positive samples")
    parser.add_argument("--splits", default=[1.0, 0.0, 0.0], type=float, nargs="*",
                        help="The ratio of samples in datasets. [1.0, 0.0, 0.0] means 60%% samples used for training, 20%% for evaluation and 20%% for test.")
    parser.add_argument("--task_type", choices=['ext', 'cls'], default="ext", type=str,
                        help="Select task type, ext for the extraction task and cls for the classification task, defaults to ext.")
    parser.add_argument("--options", default=["正向", "负向"], type=str, nargs="+",
                        help="Used only for the classification task, the options for classification")
    parser.add_argument("--prompt_prefix", default="情感倾向", type=str,
                        help="Used only for the classification task, the prompt prefix for classification")
    parser.add_argument("--is_shuffle", default=True, type=bool,
                        help="Whether to shuffle the labeled dataset, defaults to True.")
    parser.add_argument("--seed", type=int, default=1000,
                        help="random seed for initialization")

    args = parser.parse_args()
    # yapf: enable

    do_convert()
