import json, os, requests

with open('result.json') as f:
    data = json.load(f)

tokens = data.get('data', {}).get('rank', [])
token = os.environ.get('TG_TOKEN', '')
chat_id = os.environ.get('TG_CHAT_ID', '')

if not tokens:
    print("No tokens found")
    exit(0)

for t in tokens:
    n = t.get('name','?')
    s = t.get('symbol','?')
    a = t.get('address','')
    v = t.get('volume',0)
    l = t.get('liquidity',0)
    m = t.get('market_cap',0)
    
    def f(x):
        if x >= 1e6: return f"${x/1e6:.2f}M"
        if x >= 1e3: return f"${x/1e3:.1f}K"
        return f"${x:.0f}"
    
    msg = f"🔥 LP Scout - {s}\n{n}\nVol: {f(v)} | Liq: {f(l)}\nMC: {f(m)}\nhttps://gmgn.ai/robinhood/token/{a}"
    
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        print(f"Sent: {s} ({r.status_code})")
    except Exception as e:
        print(f"Error {s}: {e}")

print(f"Done: {len(tokens)} tokens")
