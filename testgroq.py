from openai import OpenAI

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

try:
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("✅ ได้ผลลัพธ์:", response.choices[0].message.content)
except Exception as e:
    import traceback
    print("📛 ERROR:")
    traceback.print_exc()
