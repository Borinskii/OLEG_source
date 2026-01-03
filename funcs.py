#funcs.py
import requests
import json
from environs import Env

# Load environment variables ONCE
env = Env()
env.read_env()

# Fireworks AI configuration
FIREWORKS_API_KEY = env.str("FIREWORKS_API_KEY")
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
MODEL_NAME = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def chat(
        model: str,
        messages: list[dict],
        options: dict = None
):
    """
    Send a chat request to Fireworks AI with automatic streaming for large responses
    """
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Default generation options
    opts = {
        "max_tokens": 6000,
        "temperature": 0.7,
        "top_p": 1.0,
        "top_k": 1,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0
    }
    if options:
        opts.update(options)

    # Automatically enable streaming if max_tokens > 5000
    max_tokens = opts.get("max_tokens", 6000)
    use_streaming = max_tokens > 5000

    # Assemble payload
    payload = {
        "model": model,
        "messages": messages,
        "stream": use_streaming,
        **opts
    }

    if use_streaming:
        # Handle streaming response
        resp = requests.post(FIREWORKS_API_URL, headers=headers, json=payload, stream=True)
        if resp.status_code != 200:
            raise RuntimeError(f"Fireworks API error {resp.status_code}: {resp.text}")

        # Collect streamed chunks
        full_response = ""
        for line in resp.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    chunk_data = line_text[6:]  # Remove 'data: ' prefix
                    if chunk_data.strip() == '[DONE]':
                        break
                    try:
                        chunk_json = json.loads(chunk_data)
                        if 'choices' in chunk_json and len(chunk_json['choices']) > 0:
                            delta = chunk_json['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            full_response += content
                    except json.JSONDecodeError:
                        continue  # Skip malformed chunks

        return full_response
    else:
        # Handle non-streaming response (for max_tokens <= 5000)
        resp = requests.post(FIREWORKS_API_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Fireworks API error {resp.status_code}: {resp.text}")

        data = resp.json()
        return data["choices"][0]["message"]["content"]


def load_llm(api_key=None):
    """Compatibility function - just returns model name"""
    return MODEL_NAME


def load_llm1(api_key=None):
    """Compatibility function - just returns model name"""
    return MODEL_NAME