# encoding: utf8
# date: 2025-01-13

import config
import pandas as pd
from string import ascii_uppercase
import random
import json

def get_question(domain: str, id: int, question: str, option_pairs: list[tuple[str, bool]], kind: str, question_info: dict[str, str]) -> dict:
    """根据中间结果生成问题

    Args:
        domain (str): 领域
        id (int): 问题编号
        question (str): 问题
        option_pairs (list[tuple[str, bool]]): 选项和判断值对
        kind (str): 问题类型

    Returns:
        dict: 问题
    """
    # 洗切选项
    random.shuffle(option_pairs)
    # 添加不满足选项
    not_satisfy_judge: bool = all([not judge for _, judge in option_pairs])
    option_pairs.append((config.not_satisfy, not_satisfy_judge))
    # 制作选项和答案
    options: dict[str, str] = {ascii_uppercase[i]: option for i, (option, _) in enumerate(option_pairs)}
    answer: list[str] = [ascii_uppercase[i] for i, (_, judge) in enumerate(option_pairs) if judge]
    # 问题
    item: dict = {
        config.DOMAIN: domain, # 领域
        config.ID: id + 1, # 问题编号，从1开始
        config.QUESTION: question,
        config.OPTIONS: options,
        config.ANSWER: answer, # 答案
        config.KIND: kind, # 问题类型
        config.QUESTION_INFO: question_info, # 问题信息
    }
    return item

def phrase_generate(df: pd.DataFrame, name: str, src_column: str, other_columns: list[str]) -> list[dict]:
    """生成与短语相关的问题

    Args:
        df (pd.DataFrame): 表格数据
        name (str): 表格名称，用作领域名称
        src_column (str): 问题来源列名
        other_columns (list[str]): 其他列名，用作选项

    Returns:
        list[dict]: 问题列表
    """
    # 获得判断列名
    judge_columns: list[str] = [i + config.judge for i in other_columns]
    # 遍历dataframe的每一行获取结果
    result: list[dict] = [] # 放置结果
    for i in range(len(df)):
        row = df.iloc[i] # 获取第i行
        # 问题生成
        question: str = config.phrase_question.replace(config.replace_symbol, row[src_column])
        # 获得短语的表达和判断值
        phrase_pairs: list[tuple[str, bool]] = list(zip(row[other_columns], row[judge_columns]))
        # 问题信息
        info: dict[str, str] = {i: row[i] for i in [config.verb, config.verb_type, config.noun_role, config.noun_type]}
        # 生成问题
        item = get_question(name, i, question, phrase_pairs, "phrase", info)
        result.append(item)
    # 返回结果
    return result

def sentence_generate(df: pd.DataFrame, name: str, columns: list[str]) -> list[dict]:
    """生成与句子相关的问题

    Args:
        df (pd.DataFrame): 表格数据
        name (str): 表格名称，用作领域名称
        columns (list[str]): 列名列表

    Returns:
        list[dict]: 问题列表
    """
    # 获得判断列名
    judge_columns: list[str] = [i + config.judge for i in columns]
    # 遍历dataframe的每一行
    result: list[dict] = [] # 放置结果
    for i in range(len(df)):
        row = df.iloc[i] # 获取第i行
        # 问题生成
        question: str = config.sentence_question
        # 获得句子的表达和判断值
        sentences_pairs: list[tuple[str, bool]] = list(zip(row[columns], row[judge_columns]))
        # 问题信息
        info: dict[str, str] = {i: row[i] for i in [config.verb, config.verb_type, config.noun_role, config.noun_type]}
        # 生成问题
        item = get_question(name, i, question, sentences_pairs, "sentence", info)
        result.append(item)
    # 返回结果
    return result

def meaning_generate(df: pd.DataFrame, name: str) -> list[dict]:
    """生成与语言意义相关的试题

    Args:
        df (pd.DataFrame): 表格数据
        name (str): 表格名称，用作领域名称

    Returns:
        list[dict]: 问题列表
    """
    # 获得列名和对应的判断列名
    columns: list[str] = [config.subject_phrase1, config.subject_phrase2]
    judge_columns: list[str] = [i + config.judge for i in columns]
    # 遍历dataframe的每一行
    result: list[dict] = [] # 放置结果
    for i in range(len(df)):
        row = df.iloc[i] # 获取第i行
        # 问题生成
        question: str = config.meaning_question.replace(config.replace_symbol, row[config.origin_form])
        # 获得句子的表达和判断值
        sentences_pairs: list[tuple[str, bool]] = list(zip(row[columns], row[judge_columns]))
        # 问题信息
        info: dict[str, str] = {i: row[i] for i in [config.verb, config.verb_type, config.noun_role, config.noun_type]}
        # 生成问题
        item = get_question(name, i, question, sentences_pairs, "meaning", info)
        result.append(item)
    # 返回结果
    return result

def question_generate(df: pd.DataFrame, name: str) -> list[dict]:
    """根据不同的表格和表格名称生成问题

    Args:
        df (pd.DataFrame): 表格数据
        name (str): 表格名称

    Raises:
        ValueError: 未知的sheet名称

    Returns:
        list[dict]: 问题列表
    """
    if name in [config.middle_location, config.middle_patient]:
        phrase_res = phrase_generate(df, name, config.middle_phrase, [config.pre_phrase, config.post_phrase, config.subject_phrase2])
        sentence_res = sentence_generate(df, name, [config.pre_sentence, config.middle_sentence, config.post_sentence])
        meaning_res = meaning_generate(df, name)
        return phrase_res + sentence_res + meaning_res
    elif name in [config.middle_agent]:
        phrase_res = phrase_generate(df, name, config.middle_phrase, [config.pre_phrase, config.post_phrase, config.subject_phrase2])
        sentence_res = sentence_generate(df, name, [config.pre_sentence, config.middle_sentence, config.post_sentence])
        return phrase_res + sentence_res
    elif name in [config.post_patient]:
        phrase_res = phrase_generate(df, name, config.post_phrase, [config.pre_phrase, config.middle_phrase, config.subject_phrase2])
        sentence_res = sentence_generate(df, name, [config.pre_sentence, config.middle_sentence, config.post_sentence])
        meaning_res = meaning_generate(df, name)
        return phrase_res + sentence_res + meaning_res
    elif name in [config.post_agent]:
        phrase_res = phrase_generate(df, name, config.post_phrase, [config.pre_phrase, config.middle_phrase, config.subject_phrase2])
        sentence_res = sentence_generate(df, name, [config.pre_sentence, config.middle_sentence, config.post_sentence])
        return phrase_res + sentence_res
    elif name in [config.pre_patient, config.pre_other]:
        phrase_res = phrase_generate(df, name, config.pre_phrase, [config.middle_phrase, config.post_phrase, config.subject_phrase2])
        sentence_res = sentence_generate(df, name, [config.pre_sentence, config.middle_sentence, config.post_sentence])
        meaning_res = meaning_generate(df, name)
        return phrase_res + sentence_res + meaning_res
    elif name in [config.subject_agent, config.subject_patient]:
        phrase_res = phrase_generate(df, name, config.subject_phrase1, [config.middle_phrase, config.post_phrase, config.pre_phrase])
        sentence_res = sentence_generate(df, name, [config.subject_sentence, config.pre_sentence, config.middle_sentence, config.post_sentence])
        return phrase_res + sentence_res
    else:
        raise ValueError(f"未知的sheet名称{name}")

def main() -> None:
    """主函数
    """
    result: list[dict] = []
    # 读取excel文件中的每一个sheet，生成问题
    for sheet in config.sheets:
        df = pd.read_excel(config.excel_path, sheet_name=sheet)
        result.extend(question_generate(df, sheet))
    # 保存结果
    with open(config.json_path, 'w', encoding='utf8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()