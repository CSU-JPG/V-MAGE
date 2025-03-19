import re

# 定义读取日志文件并提取分数的函数
def extract_scores(log_file_path):
    scores = []
    # 使用正则表达式匹配 "Game Over, You got XX score"
    score_pattern = re.compile(r"INFO:root:Game Over, You got (\d+) score")
    
    # 打开并读取日志文件
    with open(log_file_path, 'r') as file:
        for line in file:
            match = score_pattern.search(line)
            if match:
                scores.append(int(match.group(1)))
    
    return scores

# 定义计算统计值的函数
def calculate_statistics(scores):
    if not scores:
        return None, None, None
    return min(scores), max(scores), sum(scores) / len(scores)

# 主函数
def main(log_file_path):
    scores = extract_scores(log_file_path)
    if scores:
        min_score, max_score, avg_score = calculate_statistics(scores)
        print(f"分数：{scores}")
        print(f"最小值: {min_score}")
        print(f"最大值: {max_score}")
        print(f"均值: {avg_score:.2f}")
    else:
        print("未找到任何得分记录") 

if __name__ == "__main__":
    # 运行主函数，替换为你的日志文件路径
    log_file_path = input("Input the log file path: ")
    main(log_file_path)
