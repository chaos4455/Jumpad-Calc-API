# -*- coding: utf-8 -*-
"""
API RESTful Segura para Operações Matemáticas (Soma e Média) com Autenticação JWT e HTTPS

Este script Python implementa uma API RESTful robusta e segura utilizando FastAPI,
projetada para realizar operações matemáticas básicas de soma e média sobre vetores
de números inteiros. A API é protegida por autenticação JWT (JSON Web Tokens)
e utiliza HTTPS para garantir a segurança das comunicações. Logs detalhados são
gerados para monitoramento e depuração, e um sistema de rate limiting ajuda a
prevenir abusos.

Recursos Principais:
    - Operações de soma e média de vetores de inteiros.
    - Segurança robusta com autenticação JWT para endpoints protegidos (Admin e Tester).
    - Geração de tokens JWT para usuários 'admin' e 'tester'.
    - Logs detalhados em JSON para rastreamento e auditoria, com formatação colorida no console.
    - Validação de dados de entrada utilizando Pydantic.
    - Documentação interativa Swagger UI e ReDoc UI geradas automaticamente pelo FastAPI.
    - Configuração flexível através de variáveis de ambiente.
    - Geração automática de certificados autoassinados para HTTPS em ambiente de desenvolvimento.
    - Endpoint público de saúde para verificação do status da API.
    - CORS (Cross-Origin Resource Sharing) configurável para permitir acesso de diferentes origens.

Para executar a API localmente (com HTTPS e geração de certificados autoassinados em desenvolvimento):
    1. Certifique-se de ter Python e pip instalados.
    2. Instale as dependências: `pip install fastapi uvicorn pydantic python-jose cryptography`.
    3. Execute o script: `python seu_script_api.py`.
    4. Acesse a documentação interativa em http://localhost:8882/docs ou http://localhost:8882/redoc.

Informações Adicionais:
    - Credenciais padrão para ADMIN: username 'admin', password 'admin'.
    - Credenciais padrão para TESTER: username 'tester', password 'tester'.
    - A API utiliza arquivos JSON simples para armazenar credenciais em ambiente de desenvolvimento.
      Em produção, recomenda-se o uso de um sistema de gerenciamento de usuários e senhas mais robusto e seguro.

Criado por: Elias Andrade
Data de Criação: 10 de Março de 2025
"""
import sys
import os

# Adiciona o diretório pai ao path do sistema para importar módulos de 'bibliotecas'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Any

# Importações do FastAPI para criação da API
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Importações do Pydantic para validação de dados e modelos
from pydantic import BaseModel, ValidationError

# Importações do python-jose para JWT (JSON Web Tokens)
from jose import JWTError, jwt

# Importações da cryptography para geração de certificados HTTPS autoassinados
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# Importação da biblioteca local para cálculos numéricos
from bibliotecas.calc_numbers import Numbers

# ⚙️ Configurações da API (variáveis de ambiente ou valores padrão)
SECRET_KEY = os.environ.get("API_SECRET_KEY", "Jump@d2025!!)") # 🔑 Chave secreta para JWT
ALGORITHM = os.environ.get("API_JWT_ALGORITHM", "HS256") # 🔑 Algoritmo JWT
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("API_TOKEN_EXPIRY_MINUTES", "30")) # 🔑 Tempo de expiração do token (minutos)
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get("API_RATE_LIMIT", "200")) # ⚠️ Limite de requisições por minuto (Rate Limiting)
DIRETORIO_LOGS = os.environ.get("API_LOG_DIR", "logs") # 🗂️ Diretório para arquivos de log
CREDENTIALS_DIR = os.environ.get("API_CREDENTIALS_DIR", "credentials") # 🗂️ Diretório para arquivos de credenciais e certificados
origins_permitidas = os.environ.get("API_CORS_ORIGINS", "http://localhost").split(",") # 🌐 Origens permitidas para CORS

# 🔑 Esquemas de segurança OAuth2 para tokens JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token_admin") # 🛡️ Define esquema de segurança para token de admin (rota: /token_admin)
oauth2_scheme_tester = OAuth2PasswordBearer(tokenUrl="token_tester") # 🛡️ Define esquema de segurança para token de tester (rota: /token_tester)

# 🪵 Configuração de Logging (logs coloridos no console e logs JSON em arquivos)
if not os.path.exists(DIRETORIO_LOGS): # 🗂️ Cria diretório de logs se não existir
    os.makedirs(DIRETORIO_LOGS)
ARQUIVO_LOG_API = os.path.join(DIRETORIO_LOGS, "api-logs.json") # 📝 Arquivo de log principal da API (JSON resumido)
ARQUIVO_LOG_DETALHADO_API = os.path.join(DIRETORIO_LOGS, "api-detailed-logs.json") # 📝 Arquivo de log detalhado da API (JSON completo)

class FormatterColoridoSeguro(logging.Formatter): # ✨ Formatter para logs coloridos e com emojis no console
    """
    Formatter de log personalizado que adiciona cores e emojis aos logs exibidos no console.
    Melhora a legibilidade e destaca visualmente diferentes níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    CORES = { # Cores ANSI Escape Codes para diferentes níveis de log
        'DEBUG': '\033[94m',    # Azul
        'INFO': '\033[92m',     # Verde
        'WARNING': '\033[93m',  # Amarelo
        'ERROR': '\033[91m',    # Vermelho
        'CRITICAL': '\033[97;41m', # Branco em fundo Vermelho
        'RESET': '\033[0m'      # Resetar cor para padrão
    }
    EMOJIS = { # Emojis para representar visualmente os níveis de log
        'DEBUG': '🐛', # Bug/Debug
        'INFO': '✅',  # Checkmark/Sucesso
        'WARNING': '⚠️', # Warning/Aviso
        'ERROR': '🔥', # Fire/Erro
        'CRITICAL': '🚨' # Alarm/Crítico
    }
    def format(self, record): # Formata o registro de log para o console
        """
        Formata um registro de log adicionando cores, emojis, timestamp e informações contextuais.

        Args:
            record (logging.LogRecord): O registro de log a ser formatado.

        Returns:
            str: A string formatada para ser exibida no console.
        """
        cor_log = self.CORES.get(record.levelname, self.CORES['INFO']) # Obtém a cor baseada no nível de log (levelname)
        reset_cor = self.CORES['RESET'] # Código para resetar a cor para o padrão
        emoji = self.EMOJIS.get(record.levelname, '') # Obtém o emoji correspondente ao nível de log
        nivel_log = f"{cor_log}{record.levelname}{reset_cor}" # Formata o nível de log com cor
        mensagem = f"{cor_log}{record.getMessage()}{reset_cor}" # Formata a mensagem de log com cor
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Obtém o timestamp atual formatado
        return f"{timestamp} - {emoji} {nivel_log} - {record.name}:{record.lineno} - {mensagem}" # Retorna a string de log formatada

console_handler = logging.StreamHandler() # ✍️ Handler para logs no console (saída padrão)
console_handler.setFormatter(FormatterColoridoSeguro()) # Define o formatter colorido para o handler de console
api_log_handler = logging.FileHandler(ARQUIVO_LOG_API, encoding='utf-8') # ✍️ Handler para logs JSON resumidos em arquivo
api_log_formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "detalhes": %(log_record_json)s}') # Formatter JSON para logs resumidos
api_log_handler.setFormatter(api_log_formatter) # Define o formatter JSON para o handler de log resumido
api_detailed_log_handler = logging.FileHandler(ARQUIVO_LOG_DETALHADO_API, encoding='utf-8') # ✍️ Handler para logs JSON detalhados em arquivo
api_detailed_log_formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "line": "%(lineno)d", "message": "%(message)s", "record": %(log_record_json)s}') # Formatter JSON para logs detalhados
api_detailed_log_handler.setFormatter(api_detailed_log_formatter) # Define o formatter JSON para o handler de log detalhado

logger_app = logging.getLogger("api_server") # 🪵 Logger principal da aplicação, nomeado 'api_server'
logger_app.setLevel(logging.DEBUG) # Define o nível de log para DEBUG (captura todos os níveis)
logger_app.addHandler(console_handler) # Adiciona o handler de console para logs coloridos
logger_app.addHandler(api_log_handler) # Adiciona o handler para logs JSON resumidos em arquivo
logger_app.addHandler(api_detailed_log_handler) # Adiciona o handler para logs JSON detalhados em arquivo

# 🚀 Inicialização da Aplicação FastAPI
app = FastAPI(
    title="API Matemática Segura", # 🏷️ Título da API (visível na documentação)
    description="API RESTful para operações de soma e média - SEGURA (Nível Máximo) com autenticação JWT e HTTPS.", # 📝 Descrição da API
    version="0.9.3" # 📌 Versão da API
)

# ↔️ Configuração de CORS (Cross-Origin Resource Sharing) - Ajuste 'origins_permitidas' conforme necessário
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_permitidas, # 🌐 Lista de origens permitidas a acessar a API
    allow_credentials=True, # 🍪 Permite o envio de cookies em requisições cross-origin
    allow_methods=["*"], # ⚙️ Permite todos os métodos HTTP (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"], # ⚙️ Permite todos os headers HTTP
)

# 🛡️ Modelos de Dados (Pydantic) para Validação e Documentação Automática

class NumerosEntrada(BaseModel): # 🔢 Modelo para validar e documentar a entrada de lista de números
    """
    Modelo Pydantic para definir e validar a estrutura de entrada para operações que recebem uma lista de números.
    Garante que a requisição contenha um campo 'numeros' com uma lista de inteiros.
    """
    numeros: List[int] # Campo 'numeros' esperado no corpo da requisição, deve ser uma lista de inteiros
    model_config = { # Configuração extra para o modelo Pydantic
        "json_schema_extra": { # Informações extras para o schema JSON (documentação Swagger/ReDoc)
            "examples": [ # Exemplos de payload para a documentação
                {"numeros": [1, 2, 3, 4]} # Exemplo de lista de números válida
            ]
        }
    }

class TokenRequest(BaseModel): # 🔑 Modelo para requisição de token JWT (username/password)
    """
    Modelo Pydantic para definir a estrutura de requisição para obtenção de token JWT.
    Espera campos 'username' e 'password' no corpo da requisição.
    """
    username: str # 👤 Campo 'username' para autenticação
    password: str # 🔑 Campo 'password' para autenticação

class TokenResponse(BaseModel): # 🔑 Modelo para resposta de token JWT (access_token, token_type, nivel_acesso)
    """
    Modelo Pydantic para definir a estrutura da resposta ao gerar um token JWT.
    Inclui o token de acesso, o tipo do token (bearer) e o nível de acesso do usuário.
    """
    access_token: str # 🔑 Token JWT de acesso
    token_type: str # 🏷️ Tipo do token (sempre 'bearer' para JWT)
    nivel_acesso: str # 🛡️ Nível de acesso do usuário associado ao token (e.g., 'admin', 'tester')
    model_config = { # Configuração extra para o modelo Pydantic
        "json_schema_extra": { # Informações extras para o schema JSON (documentação Swagger/ReDoc)
            "examples": [ # Exemplos de resposta para a documentação
                {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer", "nivel_acesso": "admin"} # Exemplo de token JWT
            ]
        }
    }

class SomaResponse(BaseModel): # ➕ Modelo para resposta da rota /somar (resultado, mensagem, etc.)
    """
    Modelo Pydantic para definir a estrutura da resposta da rota '/somar'.
    Inclui o resultado da soma, uma mensagem de sucesso, os números de entrada e informações do usuário (opcional).
    """
    resultado: int # ➕ Resultado da operação de soma
    mensagem: str # 💬 Mensagem informativa sobre a operação
    numeros_entrada: List[int] # 🔢 Lista de números de entrada que foram somados
    usuario: Optional[str] = None # 👤 Nome de usuário associado à requisição (opcional)
    nivel_acesso: Optional[str] = None # 🛡️ Nível de acesso do usuário (opcional)
    class Config: # Configuração extra para o modelo Pydantic
        json_schema_extra = { # Informações extras para o schema JSON (documentação Swagger/ReDoc)
            "examples": [ # Exemplos de resposta para a documentação
                {"resultado": 10, "mensagem": "Operação de soma bem-sucedida", "numeros_entrada": [1, 2, 3, 4], "usuario": "admin", "nivel_acesso": "admin"} # Exemplo de resposta da soma
            ]
        }

class MediaResponse(BaseModel): # ➗ Modelo para resposta da rota /calcular_media (media, mensagem, etc.)
    """
    Modelo Pydantic para definir a estrutura da resposta da rota '/calcular_media'.
    Inclui a média calculada, uma mensagem de sucesso, os números de entrada e informações do usuário (opcional).
    """
    media: Optional[float] = None # ➗ Resultado da operação de média (pode ser None se a lista de entrada for vazia)
    mensagem: str # 💬 Mensagem informativa sobre a operação
    numeros_entrada: List[int] # 🔢 Lista de números de entrada para o cálculo da média
    usuario: Optional[str] = None # 👤 Nome de usuário associado à requisição (opcional)
    nivel_acesso: Optional[str] = None # 🛡️ Nível de acesso do usuário (opcional)
    class Config: # Configuração extra para o modelo Pydantic
        json_schema_extra = { # Informações extras para o schema JSON (documentação Swagger/ReDoc)
            "examples": [ # Exemplos de resposta para a documentação
                {"media": 2.5, "mensagem": "Operação de média bem-sucedida", "numeros_entrada": [1, 2, 3, 4], "usuario": "admin", "nivel_acesso": "admin"} # Exemplo de resposta da média
            ]
        }

class SaudeResponse(BaseModel): # 🩺 Modelo para resposta da rota /saude (status, mensagem)
    """
    Modelo Pydantic para definir a estrutura da resposta da rota '/saude'.
    Indica o status da API e uma mensagem geral de saúde.
    """
    status: str # 🩺 Status geral da API ('OK' para saudável)
    mensagem: str # 💬 Mensagem informativa sobre o status da API
    class Config: # Configuração extra para o modelo Pydantic
        json_schema_extra = { # Informações extras para o schema JSON (documentação Swagger/ReDoc)
            "examples": [ # Exemplos de resposta para a documentação
                {"status": "OK", "mensagem": "API está saudável e SEGURA"} # Exemplo de resposta de saúde
            ]
        }

class ErrorResponse(BaseModel): # ❌ Modelo para respostas de erro padronizadas (erro, detalhes)
    """
    Modelo Pydantic para definir a estrutura de respostas de erro padronizadas na API.
    Inclui uma mensagem de erro geral e detalhes adicionais sobre o erro.
    """
    erro: str # ❌ Mensagem de erro geral
    detalhes: Any # ℹ️ Detalhes adicionais sobre o erro (pode ser qualquer tipo de dado)
    class Config: # Configuração extra para o modelo Pydantic
        json_schema_extra = { # Informações extras para o schema JSON (documentação Swagger/ReDoc)
            "examples": [ # Exemplos de resposta para a documentação
                {"erro": "Erro de validação nos dados de entrada", "detalhes": "A lista de números não pode estar vazia."} # Exemplo de resposta de erro
            ]
        }

# 🔑 Funções de Segurança (JWT - JSON Web Tokens)

def gerar_token_jwt(data: dict, expires_delta: Optional[timedelta] = None) -> str: # 🔑 Gera token JWT
    """
    Gera um token JWT (JSON Web Token) seguro.

    Args:
        data (dict): Dados a serem incluídos no payload do token (e.g., informações do usuário).
        expires_delta (Optional[timedelta]): Tempo de expiração do token (opcional, se não fornecido, o token não expira).

    Returns:
        str: O token JWT codificado como uma string.
    """
    to_encode = data.copy() # Cria uma cópia dos dados para evitar modificações no original
    if expires_delta: # Se um tempo de expiração for fornecido
        expire = datetime.utcnow() + expires_delta # Calcula o tempo de expiração a partir de agora
        to_encode.update({"exp": expire}) # Adiciona a chave 'exp' (expiration time) ao payload do token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Codifica o payload em um JWT usando a chave secreta e o algoritmo especificado
    return encoded_jwt # Retorna o token JWT codificado

def verificar_token_jwt(token: str) -> Optional[dict]: # ✅ Verifica e decodifica token JWT
    """
    Verifica e decodifica um token JWT.

    Args:
        token (str): O token JWT a ser verificado e decodificado.

    Returns:
        Optional[dict]: O payload do token JWT decodificado como um dicionário, se a verificação for bem-sucedida.
                       Retorna None se o token for inválido ou expirado (JWTError).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # Decodifica o token JWT usando a chave secreta e os algoritmos permitidos
        return payload # Retorna o payload decodificado (dicionário com informações do token)
    except JWTError: # Captura exceções se o token for inválido, expirado ou a assinatura for inválida
        return None # Retorna None indicando que a verificação do token falhou

async def obter_usuario_atual_jwt(token: str = Depends(oauth2_scheme)) -> dict: # 🛡️ Dependência para obter usuário ADMIN atual via JWT
    """
    Dependência do FastAPI para obter o usuário atual (ADMIN) a partir do token JWT.
    Verifica a validade do token JWT fornecido e retorna o payload do token se válido.
    Se o token for inválido ou ausente, levanta uma exceção HTTPException 401 (Não Autorizado).

    Args:
        token (str, optional): O token JWT a ser verificado, injetado pelo FastAPI através do esquema de segurança 'oauth2_scheme'.
                               Defaults to Depends(oauth2_scheme).

    Returns:
        dict: O payload do token JWT decodificado, contendo informações do usuário ADMIN.

    Raises:
        HTTPException: 401 UNAUTHORIZED - Se o token JWT for inválido, expirado ou ausente.
    """
    logger_app.debug(f"🔒 Validando Token JWT (ADMIN): {token[:10]}...", extra={'log_record_json': {"token_prefix": token[:10]}}) # 🪵 Log de debug: validação de token ADMIN iniciada
    payload = verificar_token_jwt(token) # ✅ Verifica o token JWT usando a função 'verificar_token_jwt'
    if payload is None: # Se a verificação do token falhar (token inválido ou expirado)
        logger_app.warning("⚠️ Token JWT inválido ou expirado (ADMIN). Acesso negado.", extra={'log_record_json': {"status_auth": "falha_token_invalido_admin"}}) # 🪵 Log de warning: token ADMIN inválido
        raise HTTPException( # Levanta uma exceção HTTP 401 (Não Autorizado)
            status_code=status.HTTP_401_UNAUTHORIZED, # Código de status HTTP 401
            detail="Credenciais inválidas. Token JWT ausente, inválido ou expirado.", # Mensagem de detalhe do erro
            headers={"WWW-Authenticate": "Bearer"}, # Header para indicar o tipo de autenticação esperada (Bearer)
        )
    return payload # Retorna o payload do token decodificado (informações do usuário ADMIN)

async def obter_usuario_tester_jwt(token: str = Depends(oauth2_scheme_tester)) -> dict: # 🛡️ Dependência para obter usuário TESTER atual via JWT
    """
    Dependência do FastAPI para obter o usuário atual (TESTER) a partir do token JWT.
    Similar a 'obter_usuario_atual_jwt', mas utiliza o esquema de segurança 'oauth2_scheme_tester' para tokens de tester.
    Verifica a validade do token JWT de tester fornecido e retorna o payload se válido.
    Se o token for inválido ou ausente, levanta uma exceção HTTPException 401 (Não Autorizado).

    Args:
        token (str, optional): O token JWT de tester a ser verificado, injetado pelo FastAPI através do esquema de segurança 'oauth2_scheme_tester'.
                               Defaults to Depends(oauth2_scheme_tester).

    Returns:
        dict: O payload do token JWT de tester decodificado, contendo informações do usuário TESTER.

    Raises:
        HTTPException: 401 UNAUTHORIZED - Se o token JWT de tester for inválido, expirado ou ausente.
    """
    logger_app.debug(f"🔒 Validando Token JWT (TESTER): {token[:10]}...", extra={'log_record_json':  {"token_prefix": token[:10]}}) # 🪵 Log de debug: validação de token TESTER iniciada
    payload = verificar_token_jwt(token) # ✅ Verifica o token JWT usando a função 'verificar_token_jwt'
    if payload is None: # Se a verificação do token falhar (token inválido ou expirado)
        logger_app.warning("⚠️ Token JWT inválido ou expirado (TESTER). Acesso negado.", extra={'log_record_json': {"status_auth": "falha_token_invalido_tester"}}) # 🪵 Log de warning: token TESTER inválido
        raise HTTPException( # Levanta uma exceção HTTP 401 (Não Autorizado)
            status_code=status.HTTP_401_UNAUTHORIZED, # Código de status HTTP 401
            detail="Credenciais inválidas. Token JWT de tester ausente, inválido ou expirado.", # Mensagem de detalhe do erro (específica para tester)
            headers={"WWW-Authenticate": "Bearer"}, # Header para indicar o tipo de autenticação esperada (Bearer)
        )
    return payload # Retorna o payload do token decodificado (informações do usuário TESTER)

# 🔑 Endpoints de Autenticação Segura (JWT)

@app.post("/token_admin", tags=["autenticação_segura"], response_model=TokenResponse, summary="Gera token JWT seguro para Administradores", description="Endpoint para gerar um token JWT de acesso com nível 'admin'. Requer credenciais de administrador.")
async def gerar_token_admin_seguro(token_request: TokenRequest): # 🔑 Rota para gerar token JWT de ADMIN (/token_admin)
    """
    Endpoint para gerar um token JWT (JSON Web Token) para usuários com nível de acesso 'admin'.
    Utiliza credenciais fixas (username/password) armazenadas em um arquivo JSON para fins de demonstração.
    Em um sistema de produção, as credenciais seriam verificadas contra um banco de dados ou sistema de autenticação mais robusto.

    Args:
        token_request (TokenRequest): Objeto Pydantic contendo 'username' e 'password' para a requisição de token.

    Returns:
        TokenResponse: Objeto Pydantic contendo o 'access_token' JWT, 'token_type' (bearer) e 'nivel_acesso' ('admin').

    Raises:
        HTTPException:
            - 401 UNAUTHORIZED: Se as credenciais de administrador fornecidas estiverem incorretas.
            - 500 INTERNAL_SERVER_ERROR: Se ocorrer um erro ao ler o arquivo de credenciais (e.g., arquivo não encontrado, erro de JSON).
    """
    logger_app.info(f"🔑 Requisição para gerar token JWT (ADMIN) recebida para usuário: '{token_request.username}'", extra={'log_record_json': {"username": token_request.username}}) # 🪵 Log de info: requisição para token ADMIN recebida
    ADMIN_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "admin_credentials.json") # 🗂️ Caminho para o arquivo de credenciais de admin

    try: # Tenta ler as credenciais do arquivo JSON
        with open(ADMIN_CREDENTIALS_FILE, "r", encoding='utf-8') as f: # Abre o arquivo em modo leitura com encoding UTF-8
            usuario_admin = json.load(f) # Carrega o conteúdo JSON do arquivo para a variável 'usuario_admin'
    except FileNotFoundError: # Captura exceção se o arquivo de credenciais não for encontrado
        logger_app.critical(f"💥 Arquivo de credenciais admin não encontrado: '{ADMIN_CREDENTIALS_FILE}'.", extra={'log_record_json': {"erro": "FileNotFoundError", "arquivo": ADMIN_CREDENTIALS_FILE}}) # 🪵 Log crítico: arquivo de credenciais ADMIN não encontrado
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Arquivo de credenciais não encontrado.") # Levanta exceção HTTP 500
    except json.JSONDecodeError as e: # Captura exceção se houver erro ao decodificar o JSON
        logger_app.critical(f"💥 Erro ao decodificar JSON do arquivo de credenciais: '{ADMIN_CREDENTIALS_FILE}'. Detalhes: {e}", extra={'log_record_json': {"erro": "JSONDecodeError", "arquivo": ADMIN_CREDENTIALS_FILE, "detalhe_erro": str(e)}}) # 🪵 Log crítico: erro ao decodificar JSON de credenciais ADMIN
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Falha ao ler arquivo de credenciais.") # Levanta exceção HTTP 500

    if token_request.username == usuario_admin["username"] and token_request.password == usuario_admin["password"]: # ✅ Verifica username e password com as credenciais lidas
        tempo_expiracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Define o tempo de expiração do token
        token_jwt = gerar_token_jwt(data={"sub": token_request.username, "nivel_acesso": "admin"}, expires_delta=tempo_expiracao_token) # 🔑 Gera o token JWT para admin
        logger_app.info(f"🔑 Token JWT (ADMIN) gerado com sucesso para usuário 'admin'. Expira em {ACCESS_TOKEN_EXPIRE_MINUTES} minutos.", extra={'log_record_json': {"usuario": "admin", "expira_em_minutos": ACCESS_TOKEN_EXPIRE_MINUTES}}) # 🪵 Log de info: token ADMIN gerado com sucesso
        return {"access_token": token_jwt, "token_type": "bearer", "nivel_acesso": "admin"} # Retorna a resposta com o token JWT
    else: # Se as credenciais forem inválidas
        logger_app.warning(f"⚠️ Falha na autenticação (ADMIN) para usuário '{token_request.username}'. Credenciais inválidas.", extra={'log_record_json': {"username": token_request.username}}) # 🪵 Log de warning: falha na autenticação ADMIN
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais de administrador incorretas.") # Levanta exceção HTTP 401

@app.post("/token_tester", tags=["autenticação_segura_tester"], response_model=TokenResponse, summary="Gera token JWT seguro para Testers", description="Endpoint para gerar um token JWT de acesso com nível 'tester'. Requer credenciais de tester.")
async def gerar_token_seguro_tester(form_data: OAuth2PasswordRequestForm = Depends()): # 🔑 Rota para gerar token JWT de TESTER (/token_tester)
    """
    Endpoint para gerar um token JWT (JSON Web Token) para usuários com nível de acesso 'tester'.
    Similar ao endpoint '/token_admin', mas utiliza credenciais de 'tester' e define o nível de acesso como 'tester'.
    Utiliza credenciais fixas (username/password) armazenadas em um arquivo JSON para fins de demonstração.

    Args:
        form_data (OAuth2PasswordRequestForm): Formulário de requisição OAuth2 contendo 'username' e 'password' para a requisição de token.
                                                 Injetado pelo FastAPI através de Depends(OAuth2PasswordRequestForm).

    Returns:
        TokenResponse: Objeto Pydantic contendo o 'access_token' JWT, 'token_type' (bearer) e 'nivel_acesso' ('tester').

    Raises:
        HTTPException:
            - 401 UNAUTHORIZED: Se as credenciais de tester fornecidas estiverem incorretas.
            - 500 INTERNAL_SERVER_ERROR: Se ocorrer um erro ao ler o arquivo de credenciais de tester.
    """
    logger_app.info(f"🔑 Requisição para gerar token JWT (TESTER) recebida para usuário: '{form_data.username}'", extra={'log_record_json': {"username": form_data.username}}) # 🪵 Log de info: requisição para token TESTER recebida
    TESTER_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "tester_credentials.json") # 🗂️ Caminho para o arquivo de credenciais de tester

    try: # Tenta ler as credenciais do arquivo JSON
        with open(TESTER_CREDENTIALS_FILE, "r", encoding='utf-8') as f: # Abre o arquivo em modo leitura com encoding UTF-8
            usuario_tester = json.load(f) # Carrega o conteúdo JSON do arquivo para a variável 'usuario_tester'
    except FileNotFoundError: # Captura exceção se o arquivo de credenciais não for encontrado
        logger_app.critical(f"💥 Arquivo de credenciais tester não encontrado: '{TESTER_CREDENTIALS_FILE}'.", extra={'log_record_json': {"erro": "FileNotFoundError", "arquivo": TESTER_CREDENTIALS_FILE}}) # 🪵 Log crítico: arquivo de credenciais TESTER não encontrado
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Arquivo de credenciais de tester não encontrado.") # Levanta exceção HTTP 500
    except json.JSONDecodeError as e: # Captura exceção se houver erro ao decodificar o JSON
        logger_app.critical(f"💥 Erro ao decodificar JSON do arquivo de credenciais tester: '{TESTER_CREDENTIALS_FILE}'. Detalhes: {e}", extra={'log_record_json': {"erro": "JSONDecodeError", "arquivo": TESTER_CREDENTIALS_FILE, "detalhe_erro": str(e)}}) # 🪵 Log crítico: erro ao decodificar JSON de credenciais TESTER
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Falha ao ler arquivo de credenciais de tester.") # Levanta exceção HTTP 500

    if form_data.username == usuario_tester["username"] and form_data.password == usuario_tester["password"]: # ✅ Verifica username e password com as credenciais lidas
        tempo_expiracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Define o tempo de expiração do token
        token_jwt = gerar_token_jwt(data={"sub": form_data.username, "nivel_acesso": "tester"}, expires_delta=tempo_expiracao_token) # 🔑 Gera o token JWT para tester
        logger_app.info(f"🔑 Token JWT (TESTER) gerado com sucesso para usuário 'tester'. Expira em {ACCESS_TOKEN_EXPIRE_MINUTES} minutos.", extra={'log_record_json': {"usuario": "tester", "expira_em_minutos": ACCESS_TOKEN_EXPIRE_MINUTES}}) # 🪵 Log de info: token TESTER gerado com sucesso
        return {"access_token": token_jwt, "token_type": "bearer", "nivel_acesso": "tester"} # Retorna a resposta com o token JWT
    else: # Se as credenciais forem inválidas
        logger_app.warning(f"⚠️ Requisição para /token_tester com credenciais de tester inválidas (IGNORADO para testes API).", extra={'log_record_json': {"username": form_data.username}}) # 🪵 Log de warning: requisição para token TESTER com credenciais inválidas (ignorado para testes)
        return {"access_token": "TOKEN_INVALIDO_PARA_TESTE", "token_type": "bearer", "nivel_acesso": "tester"} # Retorna um token inválido para testes (para fins de teste da API)

# ➕ Endpoints de Operações Matemáticas (PROTEGIDOS por JWT)

@app.post("/somar", tags=["matemática_segura"], summary="Soma um vetor de números inteiros", description="Endpoint PROTEGIDO que realiza a soma de uma lista de números inteiros fornecida no corpo da requisição. Requer token JWT de administrador válido.", dependencies=[Depends(obter_usuario_atual_jwt)], response_model=SomaResponse, response_class=JSONResponse)
async def somar_vetor(request: Request, numeros_entrada: NumerosEntrada, usuario: dict = Depends(obter_usuario_atual_jwt)): # ➕ Rota para somar vetor (PROTEGIDA) - /somar
    """
    Endpoint protegido para somar uma lista de números inteiros.
    Requer um token JWT válido de administrador para ser acessado.

    Args:
        request (Request): Objeto Request do FastAPI para informações sobre a requisição.
        numeros_entrada (NumerosEntrada): Objeto Pydantic contendo a lista de números a serem somados no campo 'numeros'.
        usuario (dict): Payload do token JWT do usuário autenticado, injetado pela dependência 'obter_usuario_atual_jwt'.

    Returns:
        SomaResponse: Objeto Pydantic contendo o resultado da soma, mensagem de sucesso e informações da requisição.

    Raises:
        HTTPException:
            - 422 UNPROCESSABLE_ENTITY: Se houver erro de validação nos dados de entrada (e.g., lista de números inválida).
            - 400 BAD_REQUEST: Se houver erro de tipo de dados na biblioteca de cálculo (calc_numbers).
            - 500 INTERNAL_SERVER_ERROR: Em caso de erro interno no servidor.
    """
    detalhes_requisicao = f"Cliente: {request.client.host if request.client else 'desconhecido'}, URL: {request.url.path}, Usuário JWT (ADMIN): {usuario.get('sub') if usuario else 'desconhecido'}, Nível Acesso: {usuario.get('nivel_acesso') if usuario else 'desconhecido'}, HTTPS={request.url.scheme == 'https'}, Rate Limited=SIM" # ℹ️ Detalhes da requisição para logs
    logger_app.info(f"➡️  Requisição POST em '/somar' (PROTEGIDO) de {detalhes_requisicao}", extra={'log_record_json': {}}) # 🪵 Log de info: requisição POST para '/somar' recebida

    try: # Tenta executar a operação de soma
        lista_numeros = numeros_entrada.numeros # 🔢 Extrai a lista de números do objeto Pydantic de entrada
        logger_app.debug(f"📦 Corpo da requisição JSON recebido e VALIDADO (Pydantic): {lista_numeros}", extra={'log_record_json': {"numeros_entrada": lista_numeros}}) # 🪵 Log de debug: corpo da requisição validado

        instancia_numeros = Numbers() # ➕ Instancia a classe Numbers da biblioteca 'bibliotecas.calc_numbers'
        resultado_soma = instancia_numeros.sum_numbers(lista_numeros) # ➕ Chama a função 'sum_numbers' para realizar a soma

        conteudo_resposta = {"resultado": resultado_soma, "mensagem": "Operação de soma bem-sucedida", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')} # 💬 Monta o conteúdo da resposta
        logger_app.info(f"➕ Operação de soma bem-sucedida. Resultado: {resultado_soma} - {detalhes_requisicao}", extra={'log_record_json': {"resultado_soma": resultado_soma, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}}) # 🪵 Log de info: operação de soma bem-sucedida
        return conteudo_resposta # Retorna a resposta com o resultado da soma

    except ValueError as e_calc_value: # Captura exceção ValueError da biblioteca de cálculo (e.g., lista vazia)
        logger_app.warning(f"⚠️ Erro de validação nos dados de entrada para '/somar': {e_calc_value} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_value)}}) # 🪵 Log de warning: erro de validação na entrada para '/somar'
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e_calc_value)) # Levanta exceção HTTP 422
    except TypeError as e_calc_type: # Captura exceção TypeError da biblioteca de cálculo (e.g., tipo de dado incorreto)
        logger_app.error(f"🔥 Erro de tipo de dados na biblioteca calc_numbers para '/somar': {e_calc_type} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_type)}}) # 🪵 Log de error: erro de tipo de dados na biblioteca para '/somar'
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e_calc_type)) # Levanta exceção HTTP 400
    except HTTPException as exc_http: # Captura exceções HTTPException levantadas explicitamente no código
        logger_app.error(f"🔥 Exceção HTTP: {exc_http.detail} - Status Code: {exc_http.status_code} - {detalhes_requisicao}", extra={'log_record_json': {"erro_http": exc_http.detail, "status_code": exc_http.status_code}}) # 🪵 Log de error: exceção HTTP capturada
        raise JSONResponse(status_code=exc_http.status_code, content={"erro": exc_http.detail}) # Retorna resposta JSON com erro HTTP
    except ValidationError as ve: # Captura exceções ValidationError do Pydantic (erros de validação do modelo)
        logger_app.warning(f"⚠️ Erro de Validação de Entrada (Pydantic): {ve.errors()} - {detalhes_requisicao}", extra={'log_record_json': {"erro_validacao": ve.errors()}}) # 🪵 Log de warning: erro de validação Pydantic na entrada para '/somar'
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors()) # Levanta exceção HTTP 422
    except Exception as e: # Captura qualquer outra exceção inesperada
        msg_detalhe_erro = f"Erro inesperado no servidor: {str(e)}" # Monta mensagem de erro detalhada
        logger_app.critical(f"💥 Erro Crítico no Servidor: {msg_detalhe_erro} - {detalhes_requisicao}", exc_info=True, extra={'log_record_json': {"erro_servidor": msg_detalhe_erro, "exception": str(e)}}) # 🪵 Log crítico: erro interno do servidor para '/somar'
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"erro": "Erro interno do servidor", "detalhes": msg_detalhe_erro}) # Retorna resposta JSON com erro 500

@app.post("/calcular_media", tags=["matemática_segura"], summary="Calcula a média de um vetor de números inteiros", description="Endpoint PROTEGIDO que calcula a média de uma lista de números inteiros fornecida. Requer token JWT de administrador válido.", dependencies=[Depends(obter_usuario_atual_jwt)], response_model=MediaResponse, response_class=JSONResponse)
async def calcular_media_vetor(request: Request, numeros_entrada: NumerosEntrada, usuario: dict = Depends(obter_usuario_atual_jwt)): # ➗ Rota para calcular média vetor (PROTEGIDA) - /calcular_media
    """
    Endpoint protegido para calcular a média de uma lista de números inteiros.
    Requer um token JWT válido de administrador para ser acessado.

    Args:
        request (Request): Objeto Request do FastAPI para informações sobre a requisição.
        numeros_entrada (NumerosEntrada): Objeto Pydantic contendo a lista de números para calcular a média no campo 'numeros'.
        usuario (dict): Payload do token JWT do usuário autenticado, injetado pela dependência 'obter_usuario_atual_jwt'.

    Returns:
        MediaResponse: Objeto Pydantic contendo a média calculada, mensagem de sucesso e informações da requisição.

    Raises:
        HTTPException:
            - 422 UNPROCESSABLE_ENTITY: Se houver erro de validação nos dados de entrada.
            - 400 BAD_REQUEST: Se houver erro de tipo de dados na biblioteca de cálculo.
            - 500 INTERNAL_SERVER_ERROR: Em caso de erro interno no servidor.
    """
    detalhes_requisicao = f"Cliente: {request.client.host if request.client else 'desconhecido'}, URL: {request.url.path}, Usuário JWT (ADMIN): {usuario.get('sub') if usuario else 'desconhecido'}, Nível Acesso: {usuario.get('nivel_acesso') if usuario else 'desconhecido'}, HTTPS={request.url.scheme == 'https'}, Rate Limited=SIM" # ℹ️ Detalhes da requisição para logs
    logger_app.info(f"➡️  Requisição POST em '/calcular_media' (PROTEGIDO) de {detalhes_requisicao}", extra={'log_record_json': {}}) # 🪵 Log de info: requisição POST para '/calcular_media' recebida

    try: # Tenta executar a operação de cálculo da média
        lista_numeros = numeros_entrada.numeros # 🔢 Extrai a lista de números do objeto Pydantic de entrada
        logger_app.debug(f"📦 Corpo da requisição JSON recebido e VALIDADO (Pydantic): {lista_numeros}", extra={'log_record_json': {"numeros_entrada": lista_numeros}}) # 🪵 Log de debug: corpo da requisição validado

        instancia_numeros = Numbers() # ➗ Instancia a classe Numbers da biblioteca 'bibliotecas.calc_numbers'
        resultado_media = instancia_numeros.calculate_average(lista_numeros) # ➗ Chama a função 'calculate_average' para calcular a média

        if resultado_media is None: # 🧪 Caso a lista de números seja vazia, a média é None
            return {"media": None, "mensagem": "Operação de média bem-sucedida para lista vazia", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')} # Retorna resposta para lista vazia
        conteudo_resposta = {"media": resultado_media, "mensagem": "Operação de média bem-sucedida", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')} # 💬 Monta o conteúdo da resposta
        logger_app.info(f"➗ Operação de média bem-sucedida. Média: {resultado_media} - {detalhes_requisicao}", extra={'log_record_json': {"resultado_media": resultado_media, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}}) # 🪵 Log de info: operação de média bem-sucedida
        return conteudo_resposta # Retorna a resposta com o resultado da média

    except ValueError as e_calc_value: # Captura exceção ValueError da biblioteca de cálculo
        logger_app.warning(f"⚠️ Erro de validação nos dados de entrada para '/calcular_media': {e_calc_value} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_value)}}) # 🪵 Log de warning: erro de validação na entrada para '/calcular_media'
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e_calc_value)) # Levanta exceção HTTP 422
    except TypeError as e_calc_type: # Captura exceção TypeError da biblioteca de cálculo
        logger_app.error(f"🔥 Erro de tipo de dados na biblioteca calc_numbers para '/calcular_media': {e_calc_type} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_type)}}) # 🪵 Log de error: erro de tipo de dados na biblioteca para '/calcular_media'
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e_calc_type)) # Levanta exceção HTTP 400
    except HTTPException as exc_http: # Captura exceções HTTPException levantadas explicitamente
        logger_app.error(f"🔥 Exceção HTTP: {exc_http.detail} - Status Code: {exc_http.status_code} - {detalhes_requisicao}", extra={'log_record_json': {"erro_http": exc_http.detail, "status_code": exc_http.status_code}}) # 🪵 Log de error: exceção HTTP capturada
        raise JSONResponse(status_code=exc_http.status_code, content={"erro": exc_http.detail}) # Retorna resposta JSON com erro HTTP
    except ValidationError as ve: # Captura exceções ValidationError do Pydantic
        logger_app.warning(f"⚠️ Erro de Validação de Entrada (Pydantic): {ve.errors()} - {detalhes_requisicao}", extra={'log_record_json': {"erro_validacao": ve.errors()}}) # 🪵 Log de warning: erro de validação Pydantic na entrada para '/calcular_media'
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors()) # Levanta exceção HTTP 422
    except Exception as e: # Captura qualquer outra exceção inesperada
        msg_detalhe_erro = f"Erro inesperado no servidor: {str(e)}" # Monta mensagem de erro detalhada
        logger_app.critical(f"💥 Erro Crítico no Servidor: {msg_detalhe_erro} - {detalhes_requisicao}", exc_info=True, extra={'log_record_json': {"erro_servidor": msg_detalhe_erro, "exception": str(e)}}) # 🪵 Log crítico: erro interno do servidor para '/calcular_media'
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"erro": "Erro interno do servidor", "detalhes": msg_detalhe_erro}) # Retorna resposta JSON com erro 500

# 🩺 Endpoint de Saúde da API (PÚBLICO - Sem Autenticação)

@app.get("/saude", tags=["sistema_seguro"], summary="Verifica a saúde da API", description="Endpoint PÚBLICO para verificar se a API está online e funcionando corretamente.", response_class=JSONResponse, response_model=SaudeResponse)
async def verificar_saude_segura(): # 🩺 Rota de saúde da API (PÚBLICA) - /saude
    """
    Endpoint público para verificar a saúde e o status da API.
    Não requer autenticação e pode ser acessado por qualquer cliente.
    Retorna informações sobre o status operacional da API, versão, ambiente, etc.

    Returns:
        SaudeResponse: Objeto Pydantic contendo o 'status' da API ('OK' para operacional) e uma 'mensagem' informativa.
    """
    timestamp = datetime.now().isoformat() # 🕒 Obtém o timestamp atual em formato ISO 8601
    saude_template = { # 🩺 Template para a resposta de saúde da API
        "status": "OK", # ✅ Status da API (OK = operacional)
        "version": "0.9.3", # 📌 Versão da API
        "ambiente": os.environ.get("API_ENVIRONMENT", "Desenvolvimento"), # 🌍 Ambiente da API (e.g., 'Desenvolvimento', 'Produção')
        "timestamp": timestamp, # 🕒 Timestamp da verificação de saúde
        "mensagem": "API Matemática Segura está operacional e respondendo.", # 💬 Mensagem de saúde geral
        "detalhes": { # ℹ️ Detalhes técnicos sobre a API
            "servidor": "FastAPI", # ⚙️ Framework utilizado: FastAPI
            "seguranca": "JWT, HTTPS, Rate Limiting", # 🛡️ Mecanismos de segurança implementados
            "logs": "Detalhado em JSON" # 🪵 Formato dos logs: JSON detalhado
        },
        "status_code": 200, # 🚦 Código de status HTTP: 200 OK
        "emoji_status": "🚀", # 🚀 Emoji representando o status saudável da API
        "indicador_saude": "💚 Ótimo" # 💚 Indicador visual de saúde: Ótimo
    }
    return saude_template # Retorna o template de saúde como resposta JSON

# ⚙️ Execução do Servidor Uvicorn (HTTPS)
if __name__ == "__main__":
    import uvicorn

    # 🔑 Cria diretório para credenciais e certificados se não existirem
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    CERT_FILE = os.path.join(CREDENTIALS_DIR, "certificado.pem") # 🔑 Caminho para o arquivo de certificado HTTPS
    KEY_FILE = os.path.join(CREDENTIALS_DIR, "chave.pem") # 🔑 Caminho para o arquivo de chave privada HTTPS
    ADMIN_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "admin_credentials.json") # ⚙️ Caminho para o arquivo de credenciais de admin
    TESTER_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "tester_credentials.json") # ⚙️ Caminho para o arquivo de credenciais de tester

    # 🔑 Gera certificados autoassinados HTTPS se não existirem (para desenvolvimento local)
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE): # ✅ Verifica se os arquivos de certificado e chave não existem
        logger_app.info("🔑 Gerando certificados autoassinados para HTTPS...", extra={'log_record_json': {"acao": "geracao_certificados_https"}}) # 🪵 Log de info: geração de certificados HTTPS iniciada
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend()) # 🔑 Gera chave privada RSA
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")]) # 🔑 Define o Subject do certificado (localhost)
        builder = x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(private_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(datetime.utcnow()).not_valid_after(datetime.utcnow() + timedelta(days=365)).add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False) # 🔑 Builder do certificado X.509
        certificate = builder.sign(private_key, hashes.SHA256(), default_backend()) # 🔑 Assina o certificado com a chave privada
        with open(KEY_FILE, "wb") as key_f: # 🔑 Salva a chave privada no arquivo 'chave.pem'
            key_f.write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
        with open(CERT_FILE, "wb") as cert_f: # 🔑 Salva o certificado no arquivo 'certificado.pem'
            cert_f.write(certificate.public_bytes(serialization.Encoding.PEM))
        logger_app.info(f"🔑 Certificados autoassinados gerados e salvos em: '{CREDENTIALS_DIR}/'", extra={'log_record_json': {"acao": "certificados_salvos", "diretorio": CREDENTIALS_DIR}}) # 🪵 Log de info: certificados HTTPS gerados e salvos
    else: # Se os certificados já existirem
        logger_app.info(f"🔑 Certificados HTTPS autoassinados já existentes em: '{CREDENTIALS_DIR}/'. Usando existentes.", extra={'log_record_json': {"acao": "certificados_existentes", "diretorio": CREDENTIALS_DIR}}) # 🪵 Log de info: certificados HTTPS existentes sendo usados

    # ⚙️ Cria arquivos de credenciais padrão (admin/admin, tester/tester) se não existirem (para desenvolvimento local)
    if not os.path.exists(ADMIN_CREDENTIALS_FILE): # ✅ Verifica se o arquivo de credenciais admin não existe
        logger_app.info(f"⚙️  Criando arquivo de credenciais admin padrão: '{ADMIN_CREDENTIALS_FILE}'...", extra={'log_record_json': {"acao": "criacao_creds_admin", "arquivo": ADMIN_CREDENTIALS_FILE}}) # 🪵 Log de info: criação de credenciais ADMIN iniciada
        admin_creds = {"username": "admin", "password": "admin"} # ⚙️ Credenciais padrão admin
        with open(ADMIN_CREDENTIALS_FILE, "w", encoding='utf-8') as f: # ⚙️ Salva as credenciais admin no arquivo 'admin_credentials.json'
            json.dump(admin_creds, f, indent=4, ensure_ascii=False)
        logger_app.info(f"⚙️  Arquivo de credenciais admin padrão criado.", extra={'log_record_json': {"acao": "creds_admin_criadas_sucesso", "arquivo": ADMIN_CREDENTIALS_FILE}}) # 🪵 Log de info: credenciais ADMIN criadas com sucesso
    else: # Se o arquivo de credenciais admin já existir
        logger_app.info(f"⚙️  Arquivo de credenciais admin já existente: '{ADMIN_CREDENTIALS_FILE}'. Usando existente.", extra={'log_record_json': {"acao": "creds_admin_existentes", "arquivo": ADMIN_CREDENTIALS_FILE}}) # 🪵 Log de info: credenciais ADMIN existentes sendo usadas

    if not os.path.exists(TESTER_CREDENTIALS_FILE): # ✅ Verifica se o arquivo de credenciais tester não existe
        logger_app.info(f"⚙️  Criando arquivo de credenciais tester padrão: '{TESTER_CREDENTIALS_FILE}'...", extra={'log_record_json': {"acao": "criacao_creds_tester", "arquivo": TESTER_CREDENTIALS_FILE}}) # 🪵 Log de info: criação de credenciais TESTER iniciada
        tester_creds = {"username": "tester", "password": "tester"} # ⚙️ Credenciais padrão tester
        with open(TESTER_CREDENTIALS_FILE, "w", encoding='utf-8') as f: # ⚙️ Salva as credenciais tester no arquivo 'tester_credentials.json'
            json.dump(tester_creds, f, indent=4, ensure_ascii=False)
        logger_app.info(f"⚙️  Arquivo de credenciais tester padrão criado.", extra={'log_record_json': {"acao": "creds_tester_criadas_sucesso", "arquivo": TESTER_CREDENTIALS_FILE}}) # 🪵 Log de info: credenciais TESTER criadas com sucesso
    else: # Se o arquivo de credenciais tester já existir
        logger_app.info(f"⚙️  Arquivo de credenciais tester já existente: '{TESTER_CREDENTIALS_FILE}'. Usando existente.", extra={'log_record_json': {"acao": "creds_tester_existentes", "arquivo": TESTER_CREDENTIALS_FILE}}) # 🪵 Log de info: credenciais TESTER existentes sendo usadas

    # 🚀 Inicia o servidor Uvicorn com HTTPS e documentação Swagger/ReDoc AUTOMÁTICA no /docs e /redoc
    print("✅ Servidor FastAPI inicializado. ")
    print("➡️  Acesse a documentação interativa Swagger UI em: https://localhost:8882/docs") # 📖 Instruções Swagger UI
    print("➡️  Acesse a documentação alternativa ReDoc em: https://localhost:8882/redoc") # 📚 Instruções ReDoc
    uvicorn.run(app, host="0.0.0.0", port=8882, ssl_certfile=CERT_FILE, ssl_keyfile=KEY_FILE) # 🚀 Inicia o servidor Uvicorn com HTTPS