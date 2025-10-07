import os
import requests
import telebot
from dotenv import load_dotenv

    # Load .env
    load_dotenv()

    BOT_TOKEN = os.getenv("TG_BOT_TOKEN") or "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE"
    NUMVERIFY_KEY = os.getenv("NUMVERIFY_KEY") or "PUT_YOUR_NUMVERIFY_KEY_HERE"

    bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

    def is_ip(s):
        parts = s.split('.')
        return len(parts) == 4 and all(p.isdigit() and 0<=int(p)<=255 for p in parts)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        text = (
            """👋 नमस्ते! मैं OSINT हेल्पर बोट हूँ.

"""
            """इस्तेमाल के निर्देश:
"""
            """• फोन नंबर भेजें (उदाहरण: +919876543210) → NumVerify से lookup
"""
            """• IP भेजें (उदाहरण: 8.8.8.8) → ip-api.com से lookup (no API key)

"""
            """सुरक्षा: अपनी API keys कभी पब्लिक रिपॉज़िटरी पर न डालें."""
        )
        bot.reply_to(message, text)

    @bot.message_handler(func=lambda m: True)
    def handle_all(message):
        text = message.text.strip()
        # Phone number heuristic: starts with + or digits and length > 6
        if text.startswith('+') or (text.isdigit() and len(text) > 6):
            # Use NumVerify (apilayer) for phone
            number = text
            if NUMVERIFY_KEY == "PUT_YOUR_NUMVERIFY_KEY_HERE" or not NUMVERIFY_KEY:
                bot.reply_to(message, "⚠️ NumVerify API key सेट नहीं है। .env में NUMVERIFY_KEY डालें।")
                return
            url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_KEY}&number={number}"
            try:
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                j = r.json()
                out = [f"🔎 Phone lookup for {number}"]
                out.append(f"Valid: {j.get('valid')}")
                out.append(f"Country: {j.get('country_name') or 'N/A'} ({j.get('country_code')})")
                out.append(f"Location: {j.get('location') or 'N/A'}")
                out.append(f"Carrier: {j.get('carrier') or 'N/A'}")
                out.append(f"Line type: {j.get('line_type') or 'N/A'}")
                bot.reply_to(message, '\n'.join(out))
            except Exception as e:
                bot.reply_to(message, f"""❌ NumVerify कॉल में error: {e}")
        elif is_ip(text):
            ip = text
            url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,isp,org,as,query,lat,lon"
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                j = r.json()
                if j.get("status") == "success":
                    out = [
                        f"""🌐 IP lookup for {ip}""",
                        f"""Location: {j.get('city')}, {j.get('regionName')}, {j.get('country')}",
                        f"""ISP: {j.get('isp') or 'N/A'}",
                        f"""Org: {j.get('org') or 'N/A'}",
                        f"""AS: {j.get('as') or 'N/A'}",
                        f"""Lat/Lon: {j.get('lat')},{j.get('lon')}"
                    ]
                else:
                    out = [f"""❌ IP lookup failed: {j.get('message','unknown')}"""]
                bot.reply_to(message, '\n'.join(out))
            except Exception as e:
                bot.reply_to(message, f"""❌ IP-API कॉल में error: {e}""")
        else:
            bot.reply_to(message, "कृपया एक फोन नंबर (+countrycode...) या एक IPv4 एड्रेस भेजें।""")

    if __name__ == '__main__':
        print("Bot चल रहा है... (Ctrl+C to stop)""")
        try:
            bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print("Stopping...""")
