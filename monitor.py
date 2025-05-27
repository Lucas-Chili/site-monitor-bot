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
                return f"✅ **Online**: {url}\nTempo: {elapsed:.2f}ms"
            else:
                return f"⚠️ **Site lento**: {url}\nTempo: {elapsed:.2f}ms (limite: {max_time}ms)"
        else:
            return f"❌ **Offline**: {url}\nStatus: {r.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ **Erro**: {url}\nMotivo: {str(e)}"

if __name__ == "__main__":
    results = [check_site(url.strip()) for url in sites]
    status_report = "\n\n".join(results)
    
    # Envia relatório completo para o Discord
    send_discord_alert(f"**Relatório de Monitoramento**\n\n{status_report}")
    
    # Falha se algum site estiver offline ou lento
    if any("❌" in result or "⚠️" in result for result in results):
        exit(1)