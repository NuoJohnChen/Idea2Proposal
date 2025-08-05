from openai import OpenAI

# base_url = os.getenv('DEEPSEEK_BASE_URL')
# api_key = os.getenv('DEEPSEEK_API_KEY') #
client = OpenAI(base_url="",
                api_key="")
# client = OpenAI(base_url="",
#                 api_key="")

 


model = "deepseek-v3-128k"#"deepseek-chat-64k"#"deepseek-chat"#"deepseek-v3"


completion = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": ""},
    ],
)

print(completion)