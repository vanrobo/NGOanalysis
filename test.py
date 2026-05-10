import ctypes
import time
import httpx
import pyperclip
import sys
import re

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5-coder:1.5b"

# Reuse connection to keep latency low
http_client = httpx.Client(timeout=10.0)

def get_active_window_title() -> str:
    """Grabs the active window title in Windows 11."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value.strip()
        return title if title else "Desktop"
    except Exception:
        return "Unknown"

def get_context_hint(window_title: str) -> str:
    """Provides specific instructions based on where the user is typing."""
    title = window_title.lower()
    if any(app in title for app in ["discord", "slack", "whatsapp", "telegram", "messenger", "chat"]):
        return "CHAT APP: Keep emotion (bahaha, lol, slang). Preserve casual tone."
    elif any(app in title for app in ["code", "cursor", "pycharm", "intellij", "vscode", "test.py"]):
        return "CODE EDITOR: Format code/variables (snake_case/camelCase). Be concise."
    elif any(app in title for app in ["word", "docs", "outlook", "mail", "notion"]):
        return "PROFESSIONAL: Use formal punctuation and proper capitalization."
    else:
        return "GENERAL: Keep the dictated tone exactly as it is."

def call_ollama(messages: list, max_tokens: int = 128) -> dict:
    """Ultra-low latency call to local Ollama instance."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.0,      # Deterministic
            "num_predict": max_tokens, 
            "num_ctx": 1024,         # Low context for high speed
            "top_k": 1,
            "top_p": 0.1             
        },
        "keep_alive": -1             # Prevent model unloading from VRAM
    }
    response = http_client.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()

def fast_python_cleaner(text: str) -> str:
    """Replaces a second LLM pass. Instantly strips AI boilerplate."""
    # Remove Markdown code blocks
    text = re.sub(r'```[a-zA-Z]*\n?', '', text)
    text = text.replace('```', '')
    # Remove AI conversational filler (e.g., "Sure! Here's the cleaned text:")
    ai_prefix_pattern = r"^(Sure[^:]*:|Here is[^:]*:|Here's[^:]*:|Okay[^:]*:|Certainly[^:]*:|Output:)\s*"
    text = re.sub(ai_prefix_pattern, '', text, flags=re.IGNORECASE)
    # Remove surrounding quotes
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1]
    return text.strip()

def process_dictation(raw_transcript: str, simulated_window: str = None):
    start_time = time.perf_counter()
    
    # 1. Context Gathering
    active_window = simulated_window if simulated_window else get_active_window_title()
    context_rule = get_context_hint(active_window)
    
    # 2. Dense System Prompt
    system_prompt = f"""You are a dictation stenographer like Wispr Flow.
Rule: {context_rule}

CORE LOGIC:
1. PHONETIC FIX: Match misheard sounds to names in the [Window] title (e.g. 'ugh raav' -> 'Aarav').
2. SEMANTIC EDIT: If user says 'X no wait Y', output only 'Y'.
3. HUMAN ELEMENT: Keep laughter (bahaha, lol) and slang. Delete only hesitation (um, uh, so).
4. VERBATIM: Do not summarize. Output ONLY the clean text."""

    # 3. Dense Few-Shotting (Teaching multiple rules in 3 small examples)
    messages = [
        {"role": "system", "content": system_prompt},
        # Example 1: Chat Context + Phonetic Fix + Question Correction
        {"role": "user", "content": f"[Window: WhatsApp - Aarav] ughra soo do you want burgers? no wait pizza?"},
        {"role": "assistant", "content": "Aarav do you want pizza?"},
        # Example 2: Emotion Preservation + Slang + Fillers
        {"role": "user", "content": f"[Window: Discord] bahahahaha yo that is crazy ummm anyway call me later"},
        {"role": "assistant", "content": "bahahahaha yo that is crazy anyway call me later"},
        # Example 3: Code Context + Correction
        {"role": "user", "content": f"[Window: VS Code] create a function called get_user, no scratch that, fetch_user"},
        {"role": "assistant", "content": "fetch_user"},
        # Real Input
        {"role": "user", "content": f"[Window: {active_window}] {raw_transcript}"}
    ]
    
    # 4. LLM Execution
    resp = call_ollama(messages)
    llm_output = resp["message"]["content"].strip()
    eval_count = resp.get("eval_count", 0)
    
    # 5. Instant Cleanup
    final_output = fast_python_cleaner(llm_output)
    
    # 6. Metrics & Clipboard
    total_ms = (time.perf_counter() - start_time) * 1000
    pyperclip.copy(final_output)
    
    print(f"\n[Window] {active_window}")
    print(f"[Raw]    {raw_transcript}")
    print(f"[Final]  {final_output}  <-- (Copied!)")
    print(f"⏱️ Latency: {total_ms:.1f}ms ({eval_count} tokens)")

def main():
    print("Pre-loading Qwen into VRAM...")
    try:
        call_ollama([{"role": "user", "content": "warmup"}], max_tokens=1)
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return

    print("\n✅ Wispr Flow Engine Ready (Local RTX 3070)")
    print("- Type normally to dictate.")
    print("- Type 'win: [Name]' to simulate a window change (e.g., 'win: WhatsApp - Aarav').")
    print("- Type 'quit' to exit.")

    current_win = "Discord"
    while True:
        try:
            user_input = input(f"\n[{current_win}] > ")
            if user_input.lower() in ['quit', 'exit']: break
            if user_input.lower().startswith("win:"):
                current_win = user_input[4:].strip()
                print(f"🔄 Window set to: {current_win}")
                continue
            
            process_dictation(user_input, current_win)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()