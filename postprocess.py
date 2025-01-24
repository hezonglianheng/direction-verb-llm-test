# encoding: utf8
# date: 2025-01-23

"""对模型的结果进行后处理，计算模型的分数和时间
"""

import config
import pandas as pd
from pathlib import Path
from typing import Any
import json
import statistics
import concurrent.futures

def compare_lists(standard: list[str], outputs: list[str]) -> bool:
    """比较两个列表是否相同

    Args:
        standard (list[str]): 比较基础
        outputs (list[str]): 比较对象

    Returns:
        bool: 是否相同
    """
    if len(standard) != len(outputs):
        return False
    sorted1 = sorted(standard)
    sorted2 = sorted(outputs)
    for s, o in zip(sorted1, sorted2):
        if s != o:
            return False
    return True

def model_score(model_name: str) -> dict[str, float | str]:
    """计算模型的分数

    Args:
        model_name (str): 模型的名字

    Returns:
        dict[str, float | str]: 模型的分数
    """
    record: dict[str, float | str] = {"model": model_name}
    result_file: Path = Path(config.extracted_dir) / f"{model_name}.json"
    with result_file.open("r", encoding="utf8") as f:
        results: list[dict[str, Any]] = json.load(f)
    be_correct = [compare_lists(i[config.ANSWER], i[config.EXTRACTED_ANSWER]) for i in results]
    record['all'] = sum(be_correct) / len(be_correct)
    for kind in [config.PHRASE, config.SENTENCE, config.MEANING]:
        certain_kind = [i for i in results if i[config.KIND] == kind]
        be_correct = [compare_lists(i[config.ANSWER], i[config.EXTRACTED_ANSWER]) for i in certain_kind]
        record[kind] = sum(be_correct) / len(be_correct)
    for domain in [config.pre_phrase, config.middle_phrase, config.post_phrase, "NV上来"]:
        certain_domain = [i for i in results if domain in i[config.DOMAIN]]
        be_correct = [compare_lists(i[config.ANSWER], i[config.EXTRACTED_ANSWER]) for i in certain_domain]
        record[domain] = sum(be_correct) / len(be_correct)
    return record

def model_time(model_name: str) -> dict[str, float | str]:
    """计算模型的时间

    Args:
        model_name (str): 模型的名字

    Returns:
        dict[str, float | str]: 模型的时间
    """
    record: dict[str, str|float] = {"model": model_name}
    result_file: Path = Path(config.extracted_dir) / f"{model_name}.json"
    with result_file.open("r", encoding="utf8") as f:
        results: list[dict[str, Any]] = json.load(f)
    record['all'] = statistics.mean([i[config.TIME] for i in results])
    for kind in [config.PHRASE, config.SENTENCE, config.MEANING]:
        certain_kind = [i for i in results if i[config.KIND] == kind]
        record[kind] = statistics.mean([i[config.TIME] for i in certain_kind])
    return record

def json2dataframe(model_name: str) -> pd.DataFrame:
    """将json文件转换为dataframe

    Args:
        model_name (str): 模型的名字

    Returns:
        pd.DataFrame: dataframe
    """
    result_file: Path = Path(config.extracted_dir) / f"{model_name}.json"
    with result_file.open("r", encoding="utf8") as f:
        results: list[dict[str, Any]] = json.load(f)
    transformed = []
    for result in results:
        transformed.append({
            config.DOMAIN: result[config.DOMAIN],
            config.ID: result[config.ID],
            config.QUESTION: result[config.QUESTION],
        } | result[config.OPTIONS] |
        {
            config.ANSWER: ";".join(result[config.ANSWER]),
            config.EXTRACTED_ANSWER: ";".join([str(i) for i in result[config.EXTRACTED_ANSWER]]),
            config.JUDGE: compare_lists(result[config.ANSWER], result[config.EXTRACTED_ANSWER]),
            config.TIME: result[config.TIME],
            config.KIND: result[config.KIND], 
        } | result[config.QUESTION_INFO] | 
        {
            config.RESPONSE: result[config.RESPONSE],
        })
    return pd.DataFrame(transformed)

def basic_info() -> pd.DataFrame:
    with open(config.json_path, "r", encoding="utf8") as f:
        questions: list[dict[str, Any]] = json.load(f)
    info: list[dict[str, str|int]] = []
    for domain in [config.pre_phrase, config.middle_phrase, config.post_phrase, "NV上来"]:
        domain_info: dict[str, str|int] = {}
        for kind in [config.PHRASE, config.SENTENCE, config.MEANING]:
            certain_question = [i for i in questions if domain in i[config.DOMAIN] and i[config.KIND] == kind]
            domain_info[kind] = len(certain_question)
        domain_info['all'] = sum(domain_info.values())
        domain_info = {"domain": domain} | domain_info
        info.append(domain_info)
    # 统计总数
    info_all = {}
    for kind in [config.PHRASE, config.SENTENCE, config.MEANING]:
        certain_question = [i for i in questions if i[config.KIND] == kind]
        info_all[kind] = len(certain_question)
    info_all['all'] = sum(info_all.values())
    info_all = {"domain": "all"} | info_all
    info.append(info_all)
    return pd.DataFrame(info)

def main():
    """主函数
    """
    writer = pd.ExcelWriter(config.RESULT_FILE)
    basic_info().to_excel(writer, sheet_name="基础信息", index=False)
    score_result: list[dict[str, str|float]] = []
    time_result: list[dict[str, str|float]] = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for model in config.MODEL_NAMES:
            curr_score = executor.submit(model_score, model)
            score_result.append(curr_score.result())
            curr_time = executor.submit(model_time, model)
            time_result.append(curr_time.result())
    score_df = pd.DataFrame(score_result)
    time_df = pd.DataFrame(time_result)
    score_df.to_excel(writer, sheet_name="模型分数", index=False)
    time_df.to_excel(writer, sheet_name="模型耗时", index=False)
    for model in config.MODEL_NAMES:
        df = json2dataframe(model)
        df.to_excel(writer, sheet_name=model, index=False)
    writer.close()

if __name__ == "__main__":
    main()