# encoding: utf8
# date: 2025-01-24

"""程序入口文件
"""

import xlsx2json
import callapi
import extract
import postprocess
import time

def main():
    # 读取excel文件生成问题
    time_start = time.time()
    print("测试开始！")
    print("读取excel文件生成问题...")
    xlsx2json.main()
    # 调用API获取结果
    print("调用API获取结果...")
    callapi.main()
    # 提取结果
    print("提取结果...")
    extract.main()
    # 后处理
    print("进行结果的统计和后处理...")
    postprocess.main()
    print("测试结束！")
    time_end = time.time()
    print("总共用时：", time_end - time_start, "秒")

if __name__ == "__main__":
    main()