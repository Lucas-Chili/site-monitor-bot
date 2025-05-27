import os
import requests
import time
from discord_webhook import DiscordWebhook

sites = os.getenv('SITES').split(',')
max_time = int(os.getenv('MAX_RESPONSE_TIME', 2000))
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

def send_discord_alert(message):
    if webhook_url:
        webhook = DiscordWebhook(url=webhook_url, content=message)
        webhook.execute()

def check_site(url):
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        elapsed = (time.time() - start) * 1000  # em ms
        
        if r.status_code == 200:
            if elapsed <= max_time:
                print(f"✅ {url} - {r.status_code} - {elapsed:.2f}ms")
                return True
            else:
                message = f"⚠️ **Site lento**: {url}\nTempo de resposta: {elapsed:.2f}ms (limite: {max_time}ms)"
                print(message)
                send_discord_alert(message)
                return False
        else:
            message = f"❌ **Site offline**: {url}\nStatus code: {r.status_code}"
            print(message)
            send_discord_alert(message)
            return False
            
    except requests.exceptions.RequestException as e:
        message = f"❌ **Erro ao acessar**: {url}\nErro: {str(e)}"
        print(message)
        send_discord_alert(message)
        return False

if __name__ == "__main__":
    results = [check_site(url.strip()) for url in sites]
    if not all(results):
        exit(1)  # Falha se algum site estiver offline ou lento
