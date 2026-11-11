import sys
import socket
from urllib.parse import urlparse
import requests
import re
import base64
json_support = True

# --- CORES PARA O TERMINAL FICAR BONITO E FÁCIL DE LER ---
class Cores:
    RESET = "\033[0m"
    AZUL = "\033[94m"
    VERDE = "\033[92m"
    AMARELO = "\033[93m"
    VERMELHO = "\033[91m"
    MAGENTA = "\033[95m"
    CIANO = "\033[96m"
    NEGRITO = "\033[1m"

def analisar_base64(js_text):
    padrao_b64 = r"\b[A-Za-z0-9+/]{32,}={0,2}\b"
    matches = re.findall(padrao_b64, js_text)
    for m in matches:
        try:
            dec = base64.b64decode(m).decode("utf-8", errors="ignore")
            if len(dec) > 8 and all(32 <= ord(c) < 127 for c in dec):
                print(f"    {Cores.MAGENTA}[B64 Decodificado]{Cores.RESET} {dec}")
                analisar_endpoints_escondidos(dec)
        except Exception:
            pass

def desempacotar_webpack(js_text):
    """Tenta extrair blocos de código de dentro de módulos do Webpack ou funções agrupadas."""
    print(f"    {Cores.CIANO}[*] Analisando e desempacotando blocos Webpack / Módulos...{Cores.RESET}")
    
    padrao_rotas = r'["\'](\/[a-zA-Z0-9_\-\/\.\?=&]+)["\']'
    rotas_encontradas = set(re.findall(padrao_rotas, js_text))
    
    endpoints_uteis = []
    for rota in rotas_encontradas:
        if len(rota) > 3 and not rota.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.css', '.woff', '.ico')):
            endpoints_uteis.append(rota)
            
    return endpoints_uteis

def analisar_endpoints_escondidos(texto):
    padrao_urls = r'https?:\/\/[^\s\'"<>]+'
    urls = re.findall(padrao_urls, texto)
    for u in set(urls):
        print(f"        {Cores.VERDE}↳ URL Oculta/Encontrada:{Cores.RESET} {u}")

# Validação rápida dos argumentos
if len(sys.argv) < 3:
    print(f"{Cores.VERMELHO}Uso correto: python script.py '<lista_urls_em_linhas>' 'https://site.com'{Cores.RESET}")
    sys.exit(1)

dd = sys.argv[1]
dados = dd.splitlines()

urll = sys.argv[2]
url = urlparse(urll)
hos = url.netloc

# --- FILTRO DE TERCEIROS ---
dominios_ignorados = [
    "vimeo.com", "google-analytics.com", "googletagmanager.com", 
    "cloudflare.com", "jsdelivr.net", "cdnjs.cloudflare.com", 
    "unpkg.com", "recaptcha", "stripe.com", "facebook.net"
]

alvo_critico = [
    "-----BEGIN PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY-----",
    "private_key", "privateKey", "client_secret", "clientSecret",
    "secret_key", "secretKey", "access_token", "accessToken",
    "refresh_token", "refreshToken", "authorization: bearer",
    "Authorization: Bearer", "Bearer eyJ", "password=", "passwd=",
    "aws_access_key_id", "aws_secret_access_key", "sk_live_"
]

alvo_importante = [
    "/admin", "/dashboard", "/management", "/console",
    "process.env", "import.meta.env", "supabaseUrl", "mongodb://", "postgres://"
]

alvo_informativo = [
    "/api/", "api/", "/v1/", "/v2/", "/graphql", "graphql", "webhook", "localhost"
]

hearder = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    host = socket.gethostbyname(hos)
except Exception:
    host = hos

regex_criticos = {
    "AWS Access Key": r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "AWS Secret Key": r"(?i)aws[_-]?secret[_-]?access[_-]?key[\x22\s]*[:=][\"\s]*([A-Za-z0-9/+=]{40})",
    "Google API Key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "Stripe Live Secret Key": r"\bsk_live_[0-9A-Za-z]{20,}\b",
    "JWT Token": r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_.+/=-]{5,}\b",
    "Bearer Token": r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{20,}",
    "Private Key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "Connection String": r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis):\/\/[^\/\s:@]+:[^@\s]+@",
    "Generic Secret Assignment": r"(?i)\b(?:api[_-]?key|secret[_-]?key|client[_-]?secret|access[_-]?token)\b\s*[:=]\s*[\"\'][^\"\']{12,}[\"\']"
}

# --- SEÇÃO 1: ROTAS INICIAIS JS ---
print(f"\n{Cores.NEGRITO}{Cores.AZUL}=========================================")
print("ROTAS INICIAIS JS (Validadas)")
print(f"========================================={Cores.RESET}")

urls_para_processar = []

for i in dados:
    i = i.strip()
    if not i:
        continue
    url_limpa = "https:" + i if i.startswith("//") else i
    
    if any(dom in url_limpa for dom in dominios_ignorados):
        continue
        
    urls_para_processar.append(url_limpa)
    print(f"{Cores.VERDE}[+] {url_limpa}{Cores.RESET}")

# --- SEÇÃO 2: ROTAS E DADOS ENCONTRADOS DENTRO DOS ARQUIVOS ---
print(f"\n{Cores.NEGRITO}{Cores.AZUL}=========================================")
print("DESEMPACOTAMENTO E ANÁLISE DE VULNERABILIDADES")
print(f"========================================={Cores.RESET}")

for url_limpa in urls_para_processar:
    try:
        rq = requests.get(url_limpa, headers=hearder, timeout=5)
        if rq.status_code == 200:
            js = rq.text
            linhas = js.splitlines()
            achou_critico = False

            print(f"\n{Cores.AMARELO}➔ Processando pacote:{Cores.RESET} {url_limpa}")

            # 1. Regex Críticos (Segredos/Chaves) com Linha e Contexto
            for nome_alvo, padrao in regex_criticos.items():
                for num_linha, linha in enumerate(linhas, 1):
                    if re.search(padrao, linha):
                        achou_critico = True
                        inicio_ctx = max(0, num_linha - 2)
                        fim_ctx = min(len(linhas), num_linha + 1)
                        contexto_bloco = "\n".join(linhas[inicio_ctx:fim_ctx])
                        
                        print(f"    {Cores.VERMELHO}[CRÍTICO - {nome_alvo}]{Cores.RESET}")
                        print(f"        {Cores.CIANO}linha:{Cores.RESET} {num_linha}")
                        print(f"        {Cores.CIANO}match:{Cores.RESET} {linha.strip()}")
                        print(f"        {Cores.CIANO}contexto:{Cores.RESET}\n{Cores.MAGENTA}{contexto_bloco}{Cores.RESET}")

            # 2. Decodificação de Base64 Interno
            analisar_base64(js)

            # 3. Desempacotamento Webpack (Extração de Endpoints Ocultos)
            endpoints = desempacotar_webpack(js)
            if endpoints:
                print(f"    {Cores.CIANO}[Endpoints/Rotas Ocultas Extraídas do Webpack]:{Cores.RESET}")
                for ep in sorted(list(set(endpoints)))[:15]: 
                    print(f"        {Cores.MAGENTA}→ {ep}{Cores.RESET}")

            # 4. Fallback / Palavras-chave em Linhas Críticas com Número da Linha
            if not achou_critico:
                for num_linha, linha in enumerate(linhas, 1):
                    linha_limpa = linha.strip()
                    if any(termo in linha for termo in alvo_critico):
                        print(f"    {Cores.VERMELHO}[Keyword Crítica (Linha {num_linha})]{Cores.RESET} -> {linha_limpa}")
                    elif any(termo in linha for termo in alvo_importante):
                        print(f"    {Cores.AMARELO}[Importante (Linha {num_linha})]{Cores.RESET} -> {linha_limpa}")
                    elif any(termo in linha for termo in alvo_informativo):
                        print(f"    {Cores.AZUL}[Endpoint/API (Linha {num_linha})]{Cores.RESET} -> {linha_limpa}")
    except Exception as e:
        pass
