import os
import requests
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OSINT_API_KEY = os.getenv("OSINT_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# --- Start / Help Command ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "👋 नमस्ते! मैं OSINT हेल्पर बोट हूँ.\n\n"
        "📱 इस्तेमाल के निर्देश:\n"
        "• फोन नंबर भेजें (उदाहरण: +919876543210)\n"
        "• या IP भेजें (उदाहरण: 8.8.8.8)\n\n"
        "⚠️ सुरक्षा: अपनी API keys कभी पब्लिक में शेयर न करें।"
    )
    bot.reply_to(message, text)

# --- Handle Messages ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    query = message.text.strip()
    
    if query.startswith('+') or query.isdigit():
        result = trace_number(query)
    elif '.' in query:
        result = trace_ip(query)
    else:
        result = "❌ कृपया सही नंबर या IP भेजें।"
    
    bot.reply_to(message, result)

# --- Trace Number Function ---
def trace_number(number):
    url = f"https://osint-phone-tracer-api.p.rapidapi.com/api/v2/query/{number}"
    headers = {
        "x-rapidapi-host": "osint-phone-tracer-api.p.rapidapi.com",
        "x-rapidapi-key": OSINT_API_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return f"📞 Info for {number}:\n{data}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Trace IP Function ---
def trace_ip(ip):
    url = f"http://ip-api.com/json/{ip}"
    try:
        response = requests.get(url)
        data = response.json()
        return f"🌐 IP Info:\n{data}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Run Bot ---
if __name__ == "__main__":
    bot.infinity_polling()
