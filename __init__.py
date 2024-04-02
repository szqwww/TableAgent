import requests


# 请求地址
url = 'http://127.0.0.1:5000/tts'

# 替换这些变量为你的实际数据
cha_name = '胡桃(测试)'
character_emotion = 'default'
speak_text = '你好'
text_language = '中文'
top_k = 6
top_p = 0.8
temperature = 0.8
stream = 'False'

# 构造请求的JSON数据
data = {
    "cha_name": cha_name,
    "character_emotion": character_emotion,
    "text": speak_text,
    "text_language": text_language,
    "top_k": top_k,
    "top_p": top_p,
    "temperature": temperature,
    "stream": stream,
    "save_temp": "False"
}

# 发送POST请求
response = requests.post(url, json=data)

# 检查请求是否成功
if response.status_code == 200:
    # 处理响应内容
    print("请求成功，响应内容：")
    print(response.text)
    with open('output.mp3', 'wb') as audio_file:
        audio_file.write(response.content)
else:
    print(f'请求失败，状态码：{response.status_code}')
