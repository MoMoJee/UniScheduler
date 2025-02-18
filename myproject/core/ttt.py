import ast

def parse_ai_response(ai_response):
    """
    解析AI的回复，提取建议文本和调整后的日程列表。

    参数:
        ai_response (str): AI的原始回复字符串。

    返回:
        tuple: (建议文本列表, 调整后的日程列表)
    """
    # 初始化返回值
    suggestions = []
    schedule_list = []

    # 移除可能的干扰字符（如多余的空格、换行符等）
    ai_response = ai_response.strip()

    try:
        # 使用ast.literal_eval解析整个AI回复
        data = ast.literal_eval(ai_response)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # 检查是否符合日程字典的结构
                    if all(key in item for key in ["id", "title", "start", "end", "description", "importance", "urgency"]):
                        schedule_list.append(item)
                    else:
                        suggestions.append(item)
    except (ValueError, SyntaxError) as e:
        print(f"解析错误: {e}")
        return [], []

    # 清理建议文本：剔除包含日程字段关键词的字符串及其后续字符串
    cleaned_suggestions = []
    skip_next = False
    keywords = {"id", "title", "start", "end", "description", "importance", "urgency"}

    for suggestion in suggestions:
        if skip_next:
            skip_next = False
            continue
        if any(keyword in suggestion for keyword in keywords):
            skip_next = True
            continue
        cleaned_suggestions.append(suggestion)

    return cleaned_suggestions, schedule_list


# 示例AI回复
ai_response = str([{'id': '91cb2402-41a1-4c26-8d38-ca5a903571a1', 'title': '语文课', 'start': '2025-02-19T08:00', 'end': '2025-02-19T10:00', 'description': '302教室', 'importance': 'important', 'urgency': 'urgent'}, {'id': '3dc13cac-a8b0-4a41-a21a-91e037922a51', 'title': '数学课', 'start': '2025-02-19T10:30', 'end': '2025-02-19T12:30', 'description': '303教室', 'importance': 'important', 'urgency': 'urgent'}, {'id':'190326e4-7621-4774-80bd-69767678b9a9', 'title': '打游戏', 'start': '2025-02-19T21:00', 'end': '2025-02-19T22:00', 'description': '打王者', 'importance': 'not-important', 'urgency': 'not-urgent'}, {'id': 'cb3f3d28-cd9e-49cd-97d7-f08f3c74f905', 'title': '物理作业', 'start': '2025-02-19T13:30', 'end': '2025-02-19T15:30', 'description': '有点难，但是后天交', 'importance': 'important', 'urgency': 'urgent'}, {'id': 'da2eccf5-85a7-4887-8096-4b11abb4bf9f', 'title': '洗衣服', 'start': '2025-02-19T19:30', 'end': '2025-02-19T21:00', 'description': '洗衣机', 'importance': 'not-important', 'urgency': 'not-urgent'}, {'id': '9ee9ab36-eb0f-4789-a7b0-bf309d818af7', 'title': '逛街', 'start': '2025-02-19T21:00', 'end': '2025-02-19T23:00', 'description': '开心很重要', 'importance': 'not-important', 'urgency': 'not-urgent'}, {'id': '82c470fc-7650-4736-8361-247c4a11f405', 'title': '物理考试', 'start': '2025-02-20T13:30', 'end': '2025-02-20T16:30', 'description': '', 'importance': 'important', 'urgency': 'urgent'}, {'id': 'bf442da2-67bc-4b5f-b5f4-f24dcec3b98d', 'title': '睡觉', 'start': '2025-02-19T23:00', 'end': '2025-02-20T07:00', 'description': '不想考试，睡觉去', 'importance': 'not-important', 'urgency': 'not-urgent'}, {'我的建议': '我将打游戏和逛街的时间调整到了晚上21:00以后，以确保不会影响白天的重要任务。同时将睡觉时间调整到了晚上23:00到次日早上07:00，以确保充足的睡眠时间'}])
# 调用函数解析AI回复
suggestions, schedule_list = parse_ai_response(ai_response)

# 输出结果
print("建议文本:", suggestions)
print("调整后的日程列表:", schedule_list)