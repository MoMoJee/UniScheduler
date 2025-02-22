import requests
import json

# 目标 URL
url = "https://jwxs.muc.edu.cn/main/queryMyProctorFull"

# 请求头（根据浏览器提供的信息）
headers = {
    "Cookie": "JSESSIONID=1293219; student.urpSoft.cn=aaaWqEokKdmd9-9n47xpz; route=6b0dd8d31f9d5a33a6be4ba1f6c8fbd5; selectionBar=1293219; JSESSIONID=1293219",
    "Referer": "https://jwxs.muc.edu.cn/index",
}

# POST 请求的表单数据（根据实际需要填写）
data = {
    "flag": "1"  # 示例数据，根据实际需求调整
}

# 发送 POST 请求
response = requests.post(url, headers=headers, data=data)

# 检查响应
if response.status_code == 200:
    print("请求成功！")
    print("响应内容：")
    print(response.text)  # 打印响应内容
else:
    print(f"请求失败，状态码：{response.status_code}")
    print("响应内容：")
    print(response.text)  # 打印错误信息

if response.status_code == 200:
    data = json.loads(response.text)["data"]