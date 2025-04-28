from openai import OpenAI
import json

# 主程序
def send_to_ai(dialogues, ai_choice):
    """
    读取 JSON 文件，发送到指定的 AI API，并处理返回结果。
    :param json_file_path: JSON 文件路径
    :param api_url: API 的 URL
    :param model_name: AI 模型名称
    :return: True 或 False
    """
    try:
        api_key = "sk-TtMuIWAp8PlEyylkOfC9rUag8wadaC7QgDIpNhzmXqa1QS6r"
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )

        # 调用Kimi API进行聊天
        completion = client.chat.completions.create(
            model="kimi-latest",  # 你可以根据需要选择不同的模型规格
            messages=dialogues,
            temperature=0.3,
            response_format={"type": "json_object"}, # <-- 使用 response_format 参数指定输出格式为 json_object
            max_tokens=3500
        )
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        # 返回Kimi的回复
        return {"response": completion.choices[0].message.content, "consumption": prompt_tokens + completion_tokens}

    except Exception as e:
        print(e)
        return 0



def parse_json_to_list_and_string(json_str):
    """
    将 JSON 格式的字符串转换为一个列表和一个字符串。
    :param json_str: JSON 格式的字符串
    :return: 一个包含日程项的列表和一个建议字符串
    """
    try:
        # 解析 JSON 字符串为字典
        data = json.loads(json_str)

        # 提取日程项
        schedule_list = [item for key, item in data.items() if key.isdigit()]

        # 提取建议部分
        suggestion = data.get("suggestion", "")

        return schedule_list, suggestion
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return None, None




# 示例调用
if __name__ == "__main__":
    json_file_path = "planner.json"  # 替换为你的 JSON 文件路径
    # 读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as file:
        dialogues = json.load(file)
        for dialogue in dialogues:
            dialogue["content"] = str(dialogue["content"])


    while 1:

        dialogues.append({"role": "user", "content": input("输入你的需求：")})

        reply = send_to_ai(dialogues)["response"]
        print(reply)
        schedule_list, suggestion = parse_json_to_list_and_string(reply)
        dialogues.append({"role": "assistant", "content": reply})

        # 输出结果
        print("日程列表:", schedule_list)
        print("建议内容:", suggestion)




