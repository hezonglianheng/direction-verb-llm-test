# direction-verb-llm-test
计算语言学概论期末报告中测试语料、环境及结果等
本程序使用的Python版本为[3.12.1](https://www.python.org/downloads/release/python-3121/)

## 脚本文件
- [xlsx2json.py](xlsx2json.py): 将语料收集表中的结果转为待测试的json文件
- [callapi.py](callapi.py): 调用LLM的API测试试题
- [extract.py](extract.py): 对API输出进行文本匹配，获得模型的作答
- [postprocess.py](postprocess.py): 对模型的回答进行统计等后处理

## 结果文件
- [question.json](questions.json): 待测试的问题json文件
- [result](/result/): 调用API的结果文件夹
- [extract](/extracted/): 提取答案后的结果文件夹

## excel文件
- [“上来”语料收集表.xlsx](“上来”语料收集表.xlsx): 原始语料文件
- [“上来”测试题模型结果.xlsx](“上来”测试题模型结果.xlsx): 测试结果详细

## 其他文件
- [requirements.txt](requirements.txt): Python库配置文件