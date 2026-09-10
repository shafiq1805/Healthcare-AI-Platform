import ollama


response = ollama.chat(
    model="qwen2.5:0.5b",
    messages=[
        {
            "role": "user",
            "content": "What is a patient?"
        }
    ]
)

print("========== OLLAMA TEST ==========")
print()
print(response["message"]["content"])
print()
print("==================================")
