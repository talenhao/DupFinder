import json
import argparse

def adjust_priority(data, target_path, adjustment):
    """
    调整指定路径文件的优先级
    :param data: 原始JSON数据
    :param target_path: 需要调整的路径特征（子字符串匹配）
    :param adjustment: 调整值（正数提升优先级，负数降低）
    （新增说明）最终结果会自动按优先级升序排列（数值越小优先级越高）
    """
    for group in data.values():
        for file_entry in group:
            if target_path.lower() in file_entry["path"].lower():
                # 计算新优先级（确保不小于0）
                new_priority = file_entry["priority"] - adjustment  # 调整值符号与实际效果相反
                file_entry["priority"] = max(0, new_priority)
    return data

if __name__ == "__main__":
    """
    # 提升包含 "seagate4000g" 路径的优先级（数值减少1）
    python adjust_priority.py -i duplicates.json -o adjusted.json -p "seagate4000g" -a 1

    # 降低包含 "syncthing.history" 路径的优先级（数值增加2）
    python adjust_priority.py -i duplicates.json -o adjusted.json -p "syncthing.history" -a -2
    """
    # 解析命    令行参数
    parser = argparse.ArgumentParser(description="调整重复文件优先级")
    parser.add_argument("-i", "--input", required=True, help="输入JSON文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出JSON文件路径")
    parser.add_argument("-p", "--path", required=True, help="目标路径特征（子字符串匹配）")
    parser.add_argument("-a", "--adjust", type=int, required=True, help="调整值（正数提升优先级，负数降低）")
    
    args = parser.parse_args()
    
    # 读取原始数据
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 执行调整
    adjusted_data = adjust_priority(data, args.path, args.adjust)
    
    # 保存结果
    with open(args.output, "w", encoding="utf-8") as f:
        # 新增排序逻辑（开始）
        sorted_data = {
            k: sorted(v, key=lambda x: x["priority"])
            for k, v in adjusted_data.items()
        }
        # 新增排序逻辑（结束）
        json.dump(sorted_data, f, indent=2, ensure_ascii=False)  # 修改点：使用 sorted_data
    
    print(f"优先级调整完成，结果已保存至 {args.output}")
