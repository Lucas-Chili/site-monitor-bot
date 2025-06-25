import os
import requests
import time
import json
from urllib.parse import urlparse

# Configurações
sites = os.getenv('SITES', 'https://example.com').split(',')
max_time = int(os.getenv('MAX_RESPONSE_TIME', 2000))  # ms
google_chat_webhook = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')

def send_google_chat_alert(message):
    """Envia notificação para o Google Chat"""
    if not google_chat_webhook:
        print("⚠️ Google Chat Webhook não configurado")
        return
        
    payload = {
        "text": f"🚨 **Monitor de Sites**\n\n{message}\n\n⏱ {time.strftime('%d/%m/%Y %H:%M:%S')}"
    }
    
    try:
        response = requests.post(
            google_chat_webhook,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code != 200:
            print(f"⚠️ Falha ao enviar para Google Chat: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar alerta: {str(e)}")

def check_site(url):
    """Verifica status do site"""
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        elapsed = (time.time() - start) * 1000  # ms
        
        if r.status_code == 200:
            if elapsed <= max_time:
                return f"✅ Online: {url}\nTempo: {elapsed:.2f}ms"
            return f"⚠️ Lento: {url}\nTempo: {elapsed:.2f}ms (limite: {max_time}ms)"
        return f"❌ Offline: {url}\nStatus: {r.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ Erro: {url}\nMotivo: {str(e)}"

if __name__ == "__main__":
    results = [check_site(url.strip()) for url in sites if url.strip()]
    status_report = "\n\n".join(results)
    
    # Envia relatório completo
    send_google_chat_alert(status_report)
    
    if any("❌" in result or "⚠️" in result for result in results):
        exit(1)
