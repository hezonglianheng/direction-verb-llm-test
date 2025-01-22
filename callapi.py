# encoding: utf8
# date: 2025-01-20

"""调用大模型API对问题进行测试，返回并保存结果
"""

import config
import requests
from tqdm import tqdm
import concurrent.futures
from typing import Any
import json
from pathlib import Path
import time
import random

def call_api(model_name: str, question: str, options: dict[str, str]) -> dict[str, Any]:
    """对大模型API进行单次调用，对问题进行测试

    Args:
        model_name (str): 模型名称
        question (str): 问题
        options (dict[str, str]): 选项

    Returns:
        dict: 答案
    """
    url: str = "https://api.zhizengzeng.com/v1/chat/completions"
    # 读取api
    with open(config.api_file, "r", encoding="utf8") as f:
        api_key: str = f.read().strip()
    # 创建请求头
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}", 
    }
    # 传入参数
    params: dict = {
        "model": model_name, # 模型名称
        "messages": [
            {
                "role": "user",
                "content": question + "\n" + "\n".join([f"{k}. {v}" for k, v in options.items()]),
            },
        ],
    }
    # 记录时间
    start_time = time.time()
    # 发起请求
    response = requests.post(url, headers=headers, json=params)
    # 记录时间
    end_time = time.time()
    # 获取结果
    # 改为使用try-except结构，避免出现错误时程序中断
    try:
        result: dict[str, Any] = response.json()
    except:
        result: dict[str, Any] = {}
    # 记录时间
    result[config.TIME] = end_time - start_time
    # 返回结果
    return result

def result_arrange(input: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """整理模型回复和答案，返回结果

    Args:
        input (dict[str, Any]): 向模型中输入的内容
        result (dict[str, Any]): 模型回复

    Returns:
        dict[str, Any]: 整理后的结果
    """
    # 提取模型回复
    try:
        model_response: str = result["choices"][0]["message"]["content"]
    except:
        model_response: str = ""
    # 提取答案
    pass
    # 返回结果
    return {
        config.DOMAIN : input[config.DOMAIN],
        config.ID : input[config.ID],
        config.QUESTION : input[config.QUESTION],
        config.OPTIONS : input[config.OPTIONS],
        config.ANSWER : input[config.ANSWER],
        config.RESPONSE : model_response,
        config.TIME : result[config.TIME],
        config.KIND : input[config.KIND],
        config.QUESTION_INFO : input[config.QUESTION_INFO],
    }

def call_model(model_name: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """对大模型API进行多次调用，对问题进行测试

    Args:
        model_name (str): 模型名称
        items (list[dict[str, Any]]): 问题列表

    Returns:
        list[dict[str, Any]]: 答案列表
    """
    results: list[dict[str, Any]] = []
    for item in tqdm(items, desc=f"调用模型: {model_name}"):
        # 单次调用API
        question: str = item["question"]
        options: dict[str, str] = item["options"]
        result = call_api(model_name, question, options)
        arranged_result = result_arrange(item, result)
        results.append(arranged_result)
        # 添加随机休眠
        time.sleep(random.randint(.5, 1.5))
    return results

def main():
    """主函数
    """
    # 读取json文件
    with open(config.json_path, "r", encoding="utf8") as f:
        data: list[dict[str, Any]] = json.load(f)
    # 创建线程池
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 多线程调用
        results_list = list(executor.map(call_model, config.MODEL_NAMES, [data]*len(config.MODEL_NAMES)))
    # 转为字典
    result_dict: dict[str, list] = {model_name: results for model_name, results in zip(config.MODEL_NAMES, results_list)}
    # 保存结果
    for name, results in result_dict.items():
        with open(Path(config.res_dir) / f"{name}.json", "w", encoding="utf8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()