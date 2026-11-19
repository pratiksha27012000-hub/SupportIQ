
import json
import urllib.request
import urllib.error
from getpass import getpass

API_KEY = getpass("Paste your Gemini API key: ")

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.8-flash:generateContent"
)

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Reply with exactly: GEMINI_OK"
                }
            ]
        }
    ]
}

request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    },
    method="POST"
)

print("\nTesting Gemini API...")

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

        print("HTTP Status:", response.status)
        print("Gemini Response:",
              result["candidates"][0]["content"]["parts"][0]["text"])
        print("Connection: SUCCESS")

except urllib.error.HTTPError as error:
    print("HTTP Status:", error.code)
    print("API Error:", error.read().decode("utf-8"))
    print("Connection: FAILED")

except Exception as error:
    print("Error:", str(error))
    print("Connection: FAILED")
