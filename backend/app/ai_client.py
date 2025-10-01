# simple LLM client stub - uses OPENAI_API_KEY if provided else fallback to huggingface transformers
import os
def generate_reply(prompt: str, temperature: float = 0.2):
    # For the starter repo we return a template. Integrate real LLM in full version.
    return "Hi — thanks for your message. We appreciate the feedback and will act on it."
