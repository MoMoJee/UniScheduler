import json

from core.models import UserData
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import ollama
from openai import OpenAI
import json
import uuid

# Create your views here.

def planner_index(request):
    return render(request, 'planner_index.html')

import logging
logger = logging.getLogger("logger")

# AI建议修改的代码
@csrf_exempt
@login_required
def ai_suggestions(request):
    if request.method == 'GET':
        # 获取用户的所有事件
        user_data, created = UserData.objects.get_or_create(user=request.user, key="events")
        events = json.loads(user_data.value)
        all_events = json.loads(user_data.value)
        # 遍历列表中的每个字典，移除 "groupID" 字段，节省tokens
        for event in events:
            event.pop("groupID", None)  # 如果 "groupID" 不存在，不会报错
        events = convert_time_format(events)

        # 获取规划时间范围
        user_data_planner, created = UserData.objects.get_or_create(
            user=request.user,
            key="planner",
        )


        planner_data = json.loads(user_data_planner.value)
        time_range = planner_data["ai_planning_time"]

        # 筛选在时间范围内的事件
        filtered_events = []
        if 'start' in time_range and 'end' in time_range:
            time_range_start = datetime.fromisoformat(time_range['start'])
            time_range_end = datetime.fromisoformat(time_range['end'])

            for event in events:
                event_start = datetime.fromisoformat(event['start'])
                event_end = datetime.fromisoformat(event['end'])

                # 检查事件是否完全在时间范围内
                if time_range_start <= event_start and event_end <= time_range_end:
                    filtered_events.append(event)




        json_file_path = "default_files/events.json"  # 替换为你的 JSON 文件路径
        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            dialogues = json.load(file)
            for dialogue in dialogues:
                dialogue["content"] = str(dialogue["content"])



        dialogues.append({"role": "user", "content": str(filtered_events)})

        with open("default_files/AI_setting.json", 'r', encoding='utf-8') as file:
            ai_settings = json.load(file)



        user_data, created = UserData.objects.get_or_create(user=request.user, key="setting", defaults={"value": json.dumps({"AI_setting_code": 4})})


        ai_setting = {
            "url": "https://api.moonshot.cn/v1",
            "model": "kimi-latest",
            "api": "sk-uRE0Q10kqRt1PwxLPFYV4JV0bCDaL9r588URpIP2sCEcaVuX",
            "name": "kimi-latest",
            "temperature": 0.3,
            "code": 3
        }

        for ai_setting in ai_settings:
            if ai_setting["code"] == json.loads(user_data.value)["AI_setting_code"]:
                break

        reply = ai_reply(dialogues, ai_setting)["response"]

        schedule_list, suggestion = parse_json_to_list_and_string(reply)
        dialogues.append({"role": "assistant", "content": reply})

        logger.debug(f'AI建议了：{suggestion}')
        logger.debug(f'AI计划了：{schedule_list}')


        try:
            final_suggestion = suggestion["我的建议"]
        except:
            final_suggestion = "AI什么也没说"


        # 遍历所有原始事件，更新时间或保留原始时间
        updated_events = []
        for original_event in all_events:
            matched = False
            for ai_event in schedule_list:
                if ai_event.get("id") == original_event.get("id"):
                    # 如果 AI 修改了这个事件，更新时间
                    updated_events.append({
                        "eventId": original_event["id"],
                        "newStart": ai_event["start"],
                        "newEnd": ai_event["end"]
                    })
                    # 更新 temp_events
                    planner_data["temp_events"].append({
                        "id": original_event["id"],
                        "title": original_event["title"],
                        "start": ai_event["start"],
                        "end": ai_event["end"],
                        "description": original_event["description"],
                        "importance": original_event["importance"],
                        "urgency": original_event["urgency"],
                        "groupID": original_event["groupID"]  # 存储 groupId
                    })
                    matched = True
                    break
            if not matched:
                # 如果 AI 没有修改这个事件，保留原始时间
                updated_events.append({
                    "eventId": original_event["id"],
                    "newStart": original_event["start"],
                    "newEnd": original_event["end"],
                })

            # TODO 这里还差一个逻辑，把已经修改的日程从主events剔除


            user_data_planner.value = json.dumps(planner_data)
            user_data_planner.save()

        return JsonResponse({"events": updated_events, "suggestions": final_suggestion})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# AI生成日程的代码
@csrf_exempt
@login_required
def ai_create(request):
    if request.method == 'POST':

        # 输入接收
        data = json.loads(request.body)
        user_input = data.get('input')

        group_id = data.get('group_id')

        user_planner_data, created = UserData.objects.get_or_create(
            user=request.user,
            key="planner",
        )
        # 这里其实重复获取了，后面又导入了一次，但我懒得改
        user_events_data, created = UserData.objects.get_or_create(user=request.user, key="events")
        events = json.loads(user_events_data.value)

        planner_data = json.loads(user_planner_data.value)
        ai_planning_time = planner_data['ai_planning_time']

        # 筛选在时间范围内的事件
        filtered_events = []
        if 'start' in ai_planning_time and 'end' in ai_planning_time:
            time_range_start = datetime.fromisoformat(ai_planning_time['start'])
            time_range_end = datetime.fromisoformat(ai_planning_time['end'])

            for event in events:
                event_start = datetime.fromisoformat(event['start'])
                event_end = datetime.fromisoformat(event['end'])

                # 检查事件是否完全在时间范围内
                if time_range_start <= event_start and event_end <= time_range_end:
                    filtered_events.append(event)

        for event in filtered_events:
            event.pop("groupID", None)  # 如果 "groupID" 不存在，不会报错
            event.pop("id", None)  # 如果 "groupID" 不存在，不会报错
            event.pop("groupID", None)  # 如果 "groupID" 不存在，不会报错


        # AI设置
        json_file_path = "default_files/planner.json"  # 替换为你的 JSON 文件路径
        with open(json_file_path, 'r', encoding='utf-8') as file:
            dialogues = json.load(file)
            for dialogue in dialogues:
                dialogue["content"] = str(dialogue["content"])

        with open("default_files/AI_setting.json", 'r', encoding='utf-8') as file:
            ai_settings = json.load(file)

        user_data, created = UserData.objects.get_or_create(user=request.user, key="setting", defaults={"value": json.dumps({"AI_setting_code": 4})})
        ai_setting = {
            "url": "https://api.moonshot.cn/v1",
            "model": "kimi-latest",
            "api": "sk-uRE0Q10kqRt1PwxLPFYV4JV0bCDaL9r588URpIP2sCEcaVuX",
            "name": "kimi-latest",
            "temperature": 0.3,
            "code": 3
        }

        for ai_setting in ai_settings:
            if ai_setting["code"] == json.loads(user_data.value)["AI_setting_code"]:
                break

        # 导入历史记录
        user_data, created = UserData.objects.get_or_create(
            user=request.user,
            key="planner",
            defaults={"value": json.dumps({
                "dialogue": [],
                "temp_events": []
            })}

        )

        current_time = datetime.now()
        # 将当前时间格式化为字符串，格式为：年-月-日 时:分:秒
        time_str = current_time.strftime("%Y:%m:%d:%H:%M %A")

        planner_data = json.loads(user_data.value)
        dialogues += planner_data["dialogue"]
        dialogues.append({"role": "user", "content": f"我已经确定了如下日程，请你尽量别影响这些已经安排的日程：{str(filtered_events)}"})
        dialogues.append({"role": "user", "content": f"{time_str}  {str(user_input)}"})
        logger.debug(dialogues)

        # 解析AI回复
        # reply = ai_reply(dialogues, ai_setting)["response"]


        reply = web_search_ai_reply(dialogues, ai_setting)
        # TODO 这里是联网搜索的版本，可用但有点烧钱，可以考虑本地搜索引擎。同时这里的各种逻辑还是有点问题，毕竟直接换的，也不支持别的模型。此外我会添加一个联网搜索按钮


        created_events, suggestion = parse_json_to_list_and_string(reply)

        logger.debug(f'AI说：{suggestion}')
        logger.debug(f'AI生成了：{created_events}')


        try:
            final_suggestion = suggestion["我的建议"]
        except:
            final_suggestion = reply

        # 数据库保存AI的回复


        # 更新 dialogue
        planner_data["dialogue"] += [{
                "role": "user",
                "content": str(user_input)
            },
            {
                "role": "assistant",
                "content": reply
            }
        ]


        formated_created_events = []
        for created_event in created_events:
            formated_created_events.append({
                "id": str(uuid.uuid4()),
                "title": created_event["title"],
                "start": created_event["start"],
                "end": created_event["end"],
                "description": created_event["description"],
                "importance": created_event["importance"],
                "urgency": created_event["urgency"],
                "groupID": str(group_id)  # 存储 groupId
            })



        # 更新 temp_events
        planner_data["temp_events"] = formated_created_events

        user_data.value = json.dumps(planner_data)
        user_data.save()


        return JsonResponse({"suggestions": final_suggestion, "events": created_events})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# AI生成的对话框
@csrf_exempt
@login_required
def get_previous_dialogue(request):
    if request.method == 'GET':
        # 导入历史记录
        user_data, created = UserData.objects.get_or_create(
            user=request.user,
            key="planner",
            defaults={"value": json.dumps({
                "dialogue": [],
                "temp_events": []
            })}
        )
        planner_data = json.loads(user_data.value)
        previous_dialogue = planner_data["dialogue"]
        temp_events = planner_data["temp_events"]

        formated_dialogue = []
        for message in previous_dialogue:
            if message["role"] == "user":
                formated_dialogue.append({"user": message["content"]})
            else:
                formated_dialogue.append({"ai": (json.loads(message["content"]))["suggestion"]["我的建议"]})


        return JsonResponse({"dialogue": formated_dialogue, "tempEvents": temp_events})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# 这里写的是把AI生成的临时日程合并到主数据的代码
@csrf_exempt
@login_required
def merge_temp_events(request):
    if request.method == 'POST':
        # 导入历史记录
        user_planner_data, created = UserData.objects.get_or_create(
            user=request.user,
            key="planner",
            defaults={"value": json.dumps({
                "dialogue": [],
                "temp_events": []
            })}
        )

        user_data, created = UserData.objects.get_or_create(
            user=request.user,
            key="events",
        )


        planner_data = json.loads(user_planner_data.value)
        temp_events = planner_data["temp_events"]

        events = json.loads(user_data.value)
        events += temp_events
        user_data.value = json.dumps(events)
        user_data.save()

        user_planner_data.value = json.dumps({
            "dialogue": [],
            "temp_events": [],
            "ai_planning_time": {}
        })
        # 重置planner中的字段

        user_planner_data.save()

        return JsonResponse({"status": "success"})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



# 用来标记一段时间，存入用户数据库，给AI规划用
@login_required
@csrf_exempt
def add_to_ai_planning_time(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_time = data.get('start')
            end_time = data.get('end')

            if not start_time or not end_time:
                return JsonResponse({'status': 'error', 'message': 'Missing start or end time'}, status=400)

            user_data, created = UserData.objects.get_or_create(
                user=request.user,
                key="planner",
            )

            planner_data = json.loads(user_data.value)
            planner_data['ai_planning_time'] = {
                'start': start_time,
                'end': end_time
            }

            user_data.value = json.dumps(planner_data)
            user_data.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# 批量删除日程
@login_required
@csrf_exempt
def delete_events_in_range(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_time = data.get('start')
            end_time = data.get('end')

            logger.debug(f'{start_time}, {end_time}')

            if not start_time or not end_time:
                return JsonResponse({'status': 'error', 'message': 'Missing start or end time'}, status=400)

            user_data, created = UserData.objects.get_or_create(
                user=request.user,
                key="events",
                defaults={"value": json.dumps([])}
            )
            events = json.loads(user_data.value)

            # 过滤出完全在指定时间范围内的事件
            events_to_keep = [
                event for event in events
                if not (event['start'] >= start_time and event['end'] <= end_time)
            ]

            user_data.value = json.dumps(events_to_keep)
            user_data.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)





# AI回复的代码，AI生成和AI建议都用这个
def ai_reply(dialogues, ai_setting):
    try:
        client = OpenAI(
            api_key=ai_setting["api"],
            base_url=ai_setting["url"]
        )

        # 调用Kimi API进行聊天
        completion = client.chat.completions.create(
            model=ai_setting["model"],  # 你可以根据需要选择不同的模型规格
            messages=dialogues,
            temperature=ai_setting["temperature"],
            response_format={"type": "json_object"}, # <-- 使用 response_format 参数指定输出格式为 json_object
            max_tokens=4000
        )
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        # 返回Kimi的回复
        return {"response": completion.choices[0].message.content, "consumption": prompt_tokens + completion_tokens}

    except Exception as e:
        print(e)
        return 0



from typing import *
# search 工具的具体实现，这里我们只需要返回参数即可
# TODO 正如上述，这里要改成自己的逻辑
def search_impl(arguments: Dict[str, Any]) -> Any:
    """
    在使用 Moonshot AI 提供的 search 工具的场合，只需要原封不动返回 arguments 即可，
    不需要额外的处理逻辑。

    但如果你想使用其他模型，并保留联网搜索的功能，那你只需要修改这里的实现（例如调用搜索
    和获取网页内容等），函数签名不变，依然是 work 的。

    这最大程度保证了兼容性，允许你在不同的模型间切换，并且不需要对代码有破坏性的修改。
    """
    return arguments


def web_chat(messages, ai_setting):

    client = OpenAI(
        api_key=ai_setting["api"],
        base_url=ai_setting["url"]
    )

    completion = client.chat.completions.create(
        model="kimi-latest",
        messages=messages,
        temperature=ai_setting["temperature"],
        response_format={"type": "json_object"}, # <-- 使用 response_format 参数指定输出格式为 json_object
        max_tokens=4000,
        tools=[{"type": "builtin_function", "function": {"name": "$web_search"}}]
    )
    usage = completion.usage
    choice = completion.choices[0]

    # =========================================================================
    # 通过判断 finish_reason = stop，我们将完成联网搜索流程后，消耗的 Tokens 打印出来
    if choice.finish_reason == "stop":
        logger.debug("=================联网搜索功能启用=================")
        logger.debug(f"chat_prompt_tokens:          {usage.prompt_tokens}")
        logger.debug(f"chat_completion_tokens:      {usage.completion_tokens}")
        logger.debug(f"chat_total_tokens:           {usage.total_tokens}")
        logger.debug("===============================================")
    # =========================================================================

    return choice


def web_search_ai_reply(messages, ai_setting):

    finish_reason = None
    while finish_reason is None or finish_reason == "tool_calls":
        choice = web_chat(messages, ai_setting)
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":  # <-- 判断当前返回内容是否包含 tool_calls
            messages.append(choice.message)  # <-- 我们将 Kimi 大模型返回给我们的 assistant 消息也添加到上下文中，以便于下次请求时 Kimi 大模型能理解我们的诉求
            for tool_call in choice.message.tool_calls:  # <-- tool_calls 可能是多个，因此我们使用循环逐个执行
                tool_call_name = tool_call.function.name
                tool_call_arguments = json.loads(tool_call.function.arguments)  # <-- arguments 是序列化后的 JSON Object，我们需要使用 json.loads 反序列化一下
                if tool_call_name == "$web_search":
                    tool_result = search_impl(tool_call_arguments)
                else:
                    tool_result = f"Error: unable to find tool by name '{tool_call_name}'"

                # 使用函数执行结果构造一个 role=tool 的 message，以此来向模型展示工具调用的结果；
                # 注意，我们需要在 message 中提供 tool_call_id 和 name 字段，以便 Kimi 大模型
                # 能正确匹配到对应的 tool_call。
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result),  # <-- 我们约定使用字符串格式向 Kimi 大模型提交工具调用结果，因此在这里使用 json.dumps 将执行结果序列化成字符串
                })
    return choice.message.content






@login_required
def get_temp_long_events(request):
    if request.method == 'GET':

        user_events_data, created = UserData.objects.get_or_create(user=request.user, key="events")
        user_temp_events_data, created = UserData.objects.get_or_create(user=request.user, key="planner", defaults=
        {"value": json.dumps({
            "dialogue": [],
            "temp_events": []
        })})
        planner_data = user_temp_events_data.get_value()

        temp_events = planner_data["temp_events"]
        events = user_events_data.get_value()

        all_events = temp_events + events


        # 获取用户的所有日程组
        user_data_groups, created = UserData.objects.get_or_create(user=request.user, key="events_groups")
        events_groups = json.loads(user_data_groups.value)

        if not all_events:
            all_events = []
        # 返回事件和日程组数据
        if not events_groups:
            events_groups = []

            # 返回事件和日程组数据
        return JsonResponse({"events": all_events, "events_groups": events_groups})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



from datetime import datetime, timedelta

def convert_time_format(events):
    """
    解析事件列表，将UTC时间转换为本地时间（减去8小时）。
    :param events: 事件列表，每个事件是一个字典，包含时间信息。
    :return: 转换后的时间列表。
    """
    for event in events:
        # 检查 'start' 和 'end' 时间是否为 UTC 时间（以 'Z' 结尾）
        for key in ['start', 'end']:
            if event[key].endswith('Z'):
                # 转换为 datetime 对象并减去8小时
                utc_time = datetime.fromisoformat(event[key].replace('Z', '+00:00'))
                local_time = utc_time - timedelta(hours=-8)
                # 格式化为本地时间格式
                event[key] = local_time.strftime('%Y-%m-%dT%H:%M')
    return events


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
        logger.error(f"JSON 解析错误: {e}")
        return None, None



