# LP Scout — Auto Screener Pribadi
# Screen token di GMGN trending, filter volume, kirim ke Telegram

import requests, json, time, os
from datetime import datetime

TELEGRAM_TOKEN = "8929960970:AAFh8thrilm2uHWXJnXjarmIxPTylNTDRwk"
TELEGRAM_CHAT_ID = "6303973733"
GMGN_API = "https://api.gmgn.ai/v1"

# Filter sesuai strategi lo
MIN_VOLUME_5M = 100000  # $100k minimal
MAX_VOLUME_5M = 1000000 # $1M maksimal
CHAIN = "ro"  # robinhood
CHECK_INTERVAL = 120  # detik (2 menit)

seen_tokens = set()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }, timeout=10)
    except Exception as e:
        print(f"TG error: {e}")

def screen_tokens():
    """Screen GMGN trending buat cari token bagus"""
    try:
        # Coba endpoint trending
        resp = requests.get(
            f"{GMGN_API}/trending?chain={CHAIN}&timeframe=5m&limit=30",
            headers={"Authorization": f"Bearer {os.getenv('GMGN_API_KEY', 'gmgn_3440d862bbf8db55fe56b420d269c99b')}"},
            timeout=15
        )
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        tokens = data.get("data", []) if isinstance(data, dict) else data
        
        hasil = []
        for t in tokens[:20]:
            addr = t.get("address", t.get("token", ""))
            if addr in seen_tokens:
                continue
            
            name = t.get("name", t.get("symbol", "?"))

            vol_5m = t.get("volume_5m", t.get("volume", 0)) or 0
            if isinstance(vol_5m, str):
                vol_5m = float(vol_5m)
            
            liq = t.get("liquidity", t.get("liquidity_usd", 0)) or 0
            price = t.get("price", t.get("price_usd", 0)) or 0
            mc = t.get("market_cap", 0) or 0

            if MIN_VOLUME_5M <= vol_5m <= MAX_VOLUME_5M:
                hasil.append({
                    "address": addr,
                    "name": name,
                    "volume_5m": vol_5m,
                    "liquidity": liq,
                    "price": price,
                    "market_cap": mc,
                    "url": f"https://gmgn.ai/{CHAIN}/token/{addr}"
                })
                seen_tokens.add(addr)
        
        return hasil
    
    except Exception as e:
        print(f"Screen error: {e}")
        return []

def format_alert(t):
    vol_str = f"${t['volume_5m']:,.0f}"
    liq_str = f"${t['liquidity']:,.0f}" if t['liquidity'] else "?"
    mc_str = f"${t['market_cap']:,.0f}" if t['market_cap'] else "?"
    price_str = f"${t['price']:.8f}" if t['price'] else "?"

    return f"""🔥 *LP Opportunity!*

*Token:* {t['name']}
*Volume 5m:* {vol_str}
*Liquidity:* {liq_str}
*MC:* {mc_str}
*Price:* {price_str}

*Pool:* `{t['address'][:10]}...{t['address'][-6:]}`

[GMGN]({t['url']}) | [Uniswap](https://app.uniswap.org/positions?chain={CHAIN})
"""

if __name__ == "__main__":
    send_telegram("🚀 *LP Scout Aktif!*\nScreening token setiap 2 menit...")
    print("LP Scout started. Screening every 2 minutes...")
    
    while True:
        try:
            found = screen_tokens()
            for t in found:
                msg = format_alert(t)
                send_telegram(msg)
                print(f"[{datetime.now().isoformat()}] Found: {t['name']} (vol: ${t['volume_5m']:,.0f})")
                time.sleep(1)  # delay antar notif
            
            if not found:
                print(f"[{datetime.now().isoformat()}] No new tokens matching criteria")
        
        except Exception as e:
            print(f"Loop error: {e}")
        
        time.sleep(CHECK_INTERVAL)
