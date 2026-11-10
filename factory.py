import os
import json
import random
import time
import shutil
from datetime import datetime, timedelta
from urllib import request

API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile" # Groqなら70Bの超賢いモデルが無料で爆速稼働します
OUTPUT_DIR = "generated_tools"

DATA_TYPES = ["CSV/Excel", "Local Videos", "PDF Docs", "Audio Files", "JSON Logs"]
TARGET_USERS = ["Data Analysts", "Sysadmins", "Video Editors", "Office Workers"]
CORE_ACTIONS = ["Bulk Merging", "Auto Sorting", "Format Converting", "Metadata Clean"]

def ask_groq(prompt):
    url = "https://groq.com"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }).encode("utf-8")
    
    req = request.Request(url, data=data, headers=headers, method="POST")
    try:
        with request.urlopen(req) as res:
            result = json.loads(res.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return ""

def cleanup_old_tools():
    """7日以上経過した反応ゼロのツールを自動削除"""
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
            # 反応スコアが0のまま7日経過したら削除
            if meta.get("clicks", 0) == 0 and (now - created) > timedelta(days=7):
                shutil.rmtree(path)
                print(f"Deleted expired tool: {folder}")

def run_batch():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cleanup_old_tools()
    
    # 1回の起動で10個生産（1時間おきに動かせば1日240個）
    for i in range(10):
        # 3%の狂気突然変異
        if random.random() < 0.03:
            d_type = ask_groq("Invent an obscure, hyper-specific file format or data type (1-3 words only, no quotes).").strip() or random.choice(DATA_TYPES)
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
        
        code = ask_groq(prompt)
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
            
        time.sleep(5) # 無料APIの制限回避

if __name__ == "__main__":
    run_batch()
