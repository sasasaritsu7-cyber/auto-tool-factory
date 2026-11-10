import os
import json
import random
import time
import shutil
import requests
from datetime import datetime, timedelta

API_KEY = os.environ.get("GEMINI_API_KEY")
OUTPUT_DIR = "generated_tools"

DATA_TYPES = ["CSV/Excel", "Local Videos", "PDF Docs", "Audio Files", "JSON Logs"]
TARGET_USERS = ["Data Analysts", "Sysadmins", "Video Editors", "Office Workers"]
CORE_ACTIONS = ["Bulk Merging", "Auto Sorting", "Format Converting", "Metadata Clean"]

def ask_gemini(prompt):
    # 【修正箇所】Gemini API用の正しいURLとクエリパラメータに直しました
    url = f"https://googleapis.com{API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        if res.status_code == 200:
            result = res.json()
            candidate = result["candidates"][0] # 安全のためにpopから通常参照に変更
            part = candidate["content"]["parts"][0]
            return part["text"]
        else:
            print(f"API Error {res.status_code}: {res.text}")
            return ""
    except Exception as e:
        print(f"Request Error: {e}")
        return ""

def cleanup_old_tools():
    if not os.path.exists(OUTPUT_DIR):
        return
    now = datetime.now()
    for folder in os.listdir(OUTPUT_DIR):
        path = os.path.join(OUTPUT_DIR, folder)
        meta_path = os.path.join(path, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            created = datetime.strptime(meta["created_at"], "%Y-%m-%d")
            if meta.get("clicks", 0) == 0 and (now - created) > timedelta(days=7):
                shutil.rmtree(path)
                print(f"Deleted expired tool: {folder}")

def run_batch():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cleanup_old_tools()
    
    for i in range(10):
        if random.random() < 0.03:
            d_type = ask_gemini("Invent an obscure, hyper-specific file format or data type (1-3 words only, no quotes).").strip() or random.choice(DATA_TYPES)
        else:
            d_type = random.choice(DATA_TYPES)
            
        t_user = random.choice(TARGET_USERS)
        c_action = random.choice(CORE_ACTIONS)
        
        prompt = f"""
        Write a complete, standalone single-file Python script using ONLY standard libraries.
        Target User: {t_user}
        Data Type: {d_type}
        Action: {c_action}
        Include a simulated subscription check at the top that asks for a license key from 'https://your-stripe-link.com'.
        Output ONLY raw Python code. No markdown blocks.
        """
        
        code = ask_gemini(prompt)
        if "import" in code:
            tool_id = f"tool_{int(time.time())}_{i}"
            folder = os.path.join(OUTPUT_DIR, tool_id)
            os.makedirs(folder, exist_ok=True)
            
            with open(os.path.join(folder, "main.py"), "w", encoding="utf-8") as f:
                f.write(code.replace("```python", "").replace("```", "").strip())
                
            with open(os.path.join(folder, "meta.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "genes": {"data": d_type, "user": t_user, "action": c_action},
                    "clicks": 0
                }, f, indent=2)
            print(f"Generated: {tool_id}")
            
        time.sleep(5)

if __name__ == "__main__":
    run_batch()
