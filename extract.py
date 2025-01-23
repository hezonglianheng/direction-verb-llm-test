# encoding: utf8
# date: 2025-01-23

"""从模型API的响应中提取答案
"""

import config
from tqdm import tqdm
import re
from typing import Any
from pathlib import Path
import json
import concurrent.futures

PATTERN_STRINGS: list[str] = [
    # 文本开头的字母
    r"^([A-Z])\.",
    r"\\boxed{([A-Z])}",
    r"最终答案.*?([A-Z])",
    r"正确答案.*?([A-Z])",
    r"符合.*?是.*?([A-Z])", 
    r"正确.*?是.*?([A-Z])", 
    r"恰当.*?是.*?([A-Z])", 
    r"符合.*?是.*?([A-Z]).*?和.*?([A-Z])",
    r"最准确的答案应该是.*?([A-Z])", 
    r"最贴近原意的是.*?([A-Z])",
    r"最佳选项为.*?([A-Z])",
    r"答案是.*?([A-Z])",
    r"答案选.*?([A-Z])",
    r"答案.*?([A-Z])",
    r"([A-Z])和([A-Z]).*?正确", 
    r"([A-Z])、([A-Z])、([A-Z]).*?正确", 
    r"正确选项是.*?([A-Z])",
    r"正确的选项是.*?([A-Z])",
    r"正确的句子是.*?([A-Z])",
    r"合适的答案是.*?([A-Z])",
    r"选项\s*([A-Z])\s*.*?相同",
    r"选项\s*([A-Z])\s*.*?正确",
    r"([A-Z])\s*选项.*?正确",
    r"([A-Z])\s*选项.*?恰当",
    r"([A-Z])\s*选项.*?合适",
    r"([A-Z])\s*是正确答案",
]

def answer_extract(response: str) -> list[str]:
    """从模型API的响应中提取答案

    Args:
        response (str): 模型API的响应文本

    Returns:
        list[str]: 答案列表
    """
    patterns: list[re.Pattern] = [re.compile(pattern_string, flags=re.DOTALL) for pattern_string in PATTERN_STRINGS]
    answers: list[str] = []
    # 匹配pattern获得答案
    for pattern in patterns:
        matches = pattern.findall(response)
        if matches:
            answers.extend(matches)
            break
    answers = list(set(answers))
    # 检查：如果answers中的前一个元素大于后一个元素，则截断答案
    index = len(answers)
    for i in range(1, len(answers)):
        if answers[i] < answers[i - 1]:
            index = i
            break
    return answers[:index]

def model_results_extract(model_name: str) -> None:
    """从模型对应的结果中提取答案

    Args:
        model_name (str): 模型名称
    """
    # 读取json文件
    json_file: Path = Path(config.res_dir) / f"{model_name}.json"
    with json_file.open("r", encoding="utf8") as f:
        results: list[dict[str, Any]] = json.load(f)
    add_extracted: list[dict[str, Any]] = []
    # 提取答案
    for result in tqdm(results, desc=f"提取答案: {model_name}"):
        add_extracted.append(
            {
                config.DOMAIN : result[config.DOMAIN],
                config.ID : result[config.ID],
                config.QUESTION : result[config.QUESTION],
                config.OPTIONS : result[config.OPTIONS],
                config.ANSWER : result[config.ANSWER],
                config.EXTRACTED_ANSWER : answer_extract(result[config.RESPONSE]),
                config.RESPONSE : result[config.RESPONSE],
                config.TIME : result[config.TIME],
                config.KIND : result[config.KIND],
                config.QUESTION_INFO : result[config.QUESTION_INFO],
            }
        )
    # 保存结果
    extracted_file: Path = Path(config.extracted_dir) / f"{model_name}.json"
    with extracted_file.open("w", encoding="utf8") as f:
        json.dump(add_extracted, f, ensure_ascii=False, indent=4)

def main() -> None:
    """主函数
    """
    # 创建进程池
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 多进程提取
        for model in config.MODEL_NAMES:
            executor.submit(model_results_extract, model)

if __name__ == "__main__":
    main()