# encoding: utf8
# date: 2025-01-13

"""程序配置文件"""

# 问题类型
PHRASE = "phrase"
SENTENCE = "sentence"
MEANING = "meaning"

# excel文件的相关内容
## excel文件的路径
excel_path = r'“上来”语料收集表.xlsx'
## excel文件的sheet名
### 中宾式的sheets
middle_location = r"V上N来-地点N"
middle_patient = r"V上N来-受事N"
middle_agent = r"V上N来-施事N"
### 后宾式的sheets
post_patient = r"V上来N-受事N"
post_agent = r"V上来N-施事N"
### 前宾式的sheets
pre_patient = r"VN上来-受事N"
pre_other = r"VN上来-其他N"
### 主语式的sheets
subject_agent = r"NV上来-施事N"
subject_patient = r"NV上来-受事N"
sheets = [
    middle_location,
    middle_patient,
    middle_agent,
    post_patient,
    post_agent,
    pre_patient,
    pre_other,
    subject_agent,
    subject_patient, 
]
## columns的名字
origin_form = r"原始格式"
pre_phrase = r"VN上来"
middle_phrase = r"V上N来"
post_phrase = r"V上来N"
subject_phrase1 = r"NV上来-1"
subject_phrase2 = r"NV上来-2"
judge = r"-正误"
pre_sentence = r"VN上来-全句"
middle_sentence = r"V上N来-全句"
post_sentence = r"V上来N-全句"
subject_sentence = r"NV上来-全句"
verb = r"动词"
verb_type = r"动词类型"
noun_role = r"名词角色"
noun_type = r"名词类型"
source = r"来源"

# json文件的相关内容
## json文件的路径
json_path = r'questions.json'
## json文件的key
DOMAIN = "domain"
ID = "id"
QUESTION = "question"
OPTIONS = "options"
ANSWER = "answer"
KIND = "kind"
QUESTION_INFO = "question_info"
VERB = "verb"
VERB_TYPE = "verb_type"
NOUN_ROLE = "noun_role"
NOUN_TYPE = "noun_type"
RESPONSE = "response"
EXTRACTED_ANSWER = "extracted_answer"
TIME = "time"
JUDGE = "judge"

# 提问的问题
## 替换符
replace_symbol = r"[replace]"
## 提问的问题
phrase_question = r"以下选项中符合语法且语义与“[replace]”相同的是_____"
sentence_question = r"以下选项中语法、语义正确的是_____"
meaning_question = r"以下选项中与“[replace]”意思一样的是_____"
## 以上选项均不满足题意
not_satisfy = r"以上选项均不满足题意"

# api文件
api_file = r"config/api.txt"
# 模型名称
MODEL_NAMES = [
    # "o1-preview", 
    "gpt-4o", 
    "claude-3-5-sonnet-20241022", 
    # "gemini-2.0-flash-exp", 
    "qwen2.5-72b-instruct", 
    "llama3.3-70b-instruct", 
    # "glm-4-plus", 
    # "deepseek-reasoner", 
    "deepseek-chat", 
]
# API返回结果目录
res_dir = r"result"
# API调用的url
url = "https://api.zhizengzeng.com/v1/chat/completions"
# 提取结果的目录
extracted_dir = r"extracted"

# 结果文件
RESULT_FILE = r"“上来”测试题模型结果.xlsx"