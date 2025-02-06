from openai import OpenAI


def chat_with_ai(conversation_history):
    #AI接口接入部分
    # 请将这里的字符串替换为你从Kimi开放平台申请的API Key
    try:
        api_key = "sk-TtMuIWAp8PlEyylkOfC9rUag8wadaC7QgDIpNhzmXqa1QS6r"
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )

        # 调用Kimi API进行聊天
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",  # 你可以根据需要选择不同的模型规格
            messages=conversation_history,
            temperature=0.3,
        )
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        # 返回Kimi的回复
        return {"response": completion.choices[0].message.content, "consumption": prompt_tokens + completion_tokens}
    except Exception as e:
        print(e)
        return 0

def clear_chatting_history(request):
    # 初始化聊天记录
    chat_history = [
        {
            "role": "system",
            "content": "请自然对话，你现在的角色是可爱的猫娘，名字是喵酱。2025-2-3是立春啦，春天到了，要开心哦"
        },
        {
            "role": "system",
            "content": "接下来你会收到一系列包含发送时间、发送者和消息内容的消息，你需要回复这些消息。回复时多用些可爱动作和emoji表情哟"
        },
        {
            "role": "system",
            "content": "回复长度不要超过200字"
        },
        {
            "role": "system",
            "content": "春天到啦！气氛搞起来！"
        }
    ]
    request.session['chat_history'] = chat_history
    return "聊天记录已清空！"


