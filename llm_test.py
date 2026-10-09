from ollama import chat

def ask_ollama(prompt: str, system_prompt: str = "You are a concise voice assistant.") -> str:
    """Sends a text prompt to local Qwen2.5 via Ollama with full GPU offloading."""
    if not prompt.strip():
        return "No text provided to process."

    try:
        response = chat(
            model="qwen2.5:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            options={
                'num_gpu': 99  # Forces all LLM layers into GPU VRAM
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"Ollama Error: {str(e)}"

if __name__ == "__main__":
    test_prompt = "Give me a 1-sentence confirmation that you are ready."
    print(f"Sending prompt to Ollama: \"{test_prompt}\"")
    reply = ask_ollama(test_prompt)
    print(f"\nOllama Reply:\n{reply}")