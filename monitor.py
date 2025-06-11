import os
import requests
import time
from urllib.parse import urlparse
from discord_webhook import DiscordWebhook

# Configurações
sites = os.getenv('SITES', 'https://example.com').split(',')
max_time = int(os.getenv('MAX_RESPONSE_TIME', 2000))  # ms
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
bot_identifier = 'SiteMonitorBot/1.0 (+https://github.com/your-repo)'

# Headers para evitar tracking e identificar como bot
REQUEST_HEADERS = {
    'User-Agent': bot_identifier,
    'X-Monitoring-Bot': 'true',  # Header customizado para identificação
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
}

def send_discord_alert(message):
    """Envia notificação para o Discord"""
    if webhook_url:
        try:
            webhook = DiscordWebhook(
                url=webhook_url, 
                content=message,
                rate_limit_retry=True
            )
            response = webhook.execute()
            if not response.ok:
                print(f"Erro ao enviar para Discord: {response.status_code}")
        except Exception as e:
            print(f"Falha ao enviar para Discord: {str(e)}")

def add_monitoring_params(url):
    """Adiciona parâmetros para evitar tracking"""
    parsed = urlparse(url)
    if parsed.query:
        return f"{url}&bot_monitoring=true&skip_analytics=true"
    return f"{url}?bot_monitoring=true&skip_analytics=true"

def check_site(url):
    """Verifica status do site"""
    try:
        monitoring_url = add_monitoring_params(url)
        start = time.time()
        
        # Desativa verificação SSL para evitar erros em sites com certificado inválido
        r = requests.get(
            monitoring_url,
            headers=REQUEST_HEADERS,
            timeout=10,
            allow_redirects=True,
            verify=False
        )
        
        elapsed = (time.time() - start) * 1000  # ms
        
        if r.status_code == 200:
            if elapsed <= max_time:
                return f"✅ **Online**: {url}\nTempo: {elapsed:.2f}ms"
            return f"⚠️ **Site lento**: {url}\nTempo: {elapsed:.2f}ms (limite: {max_time}ms)"
        
        return f"❌ **Erro HTTP**: {url}\nStatus: {r.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ **Falha na conexão**: {url}\nErro: {str(e)}"

def generate_report(results):
    """Gera relatório formatado"""
    status_report = "\n\n".join(results)
    return (
        "**Relatório de Monitoramento**\n\n"
        f"{status_report}\n\n"
        f"🕒 Atualizado em: {time.strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"⚙️ Bot: {bot_identifier}"
    )

if __name__ == "__main__":
    print(f"Iniciando verificação de {len(sites)} sites...")
    
    results = []
    for url in sites:
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        print(f"Verificando: {url}")
        results.append(check_site(url))
    
    report = generate_report(results)
    send_discord_alert(report)
    
    if any("❌" in result or "⚠️" in result for result in results):
        print("Falha detectada - Enviando alerta")
        exit(1)
    
    print("Todos os sites estão operacionais")
