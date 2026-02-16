from google import genai


client = genai.Client()

response = client.models.generate_content(
    model="gemini-flash-lite-latest",
    contents="Are you able to classify this as spam or ham? : Wow! amazing oprotunity! But now!",
)
print(response)
