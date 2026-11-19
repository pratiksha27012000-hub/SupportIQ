
from groq import Groq
from getpass import getpass

API_KEY = getpass("Paste your Groq API key: ")

client = Groq(
    api_key=API_KEY,
    timeout=30,
    max_retries=0
)

print("\nTesting Groq API...")

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: GROQ_OK"
            }
        ],
        temperature=0
    )

    answer = response.choices[0].message.content

    print("Model:", response.model)
    print("Response:", answer)
    print("Connection: SUCCESS")

except Exception as error:
    print("Error:", str(error))
    print("Connection: FAILED")
