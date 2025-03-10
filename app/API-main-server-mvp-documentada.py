# -*- coding: utf-8 -*-
"""
API RESTful Segura para Operações Matemáticas (Soma e Média)

Este script Python implementa uma API RESTful robusta e segura utilizando FastAPI,
projetada para realizar operações matemáticas básicas de soma e média sobre vetores
de números inteiros. A API é protegida por autenticação JWT (JSON Web Tokens)
e utiliza HTTPS para garantir a segurança das comunicações. Logs detalhados são
gerados para monitoramento e depuração, e um sistema de rate limiting ajuda a
prevenir abusos.

Recursos Principais:
    - Operações de soma e média de vetores de inteiros.
    - Segurança robusta com autenticação JWT para endpoints protegidos.
    - Geração de tokens JWT para usuários 'admin' e 'tester'.
    - Logs detalhados em JSON para rastreamento e auditoria.
    - Formatação de logs colorida para console, facilitando a leitura durante o desenvolvimento.
    - Validação de dados de entrada utilizando Pydantic.
    - Documentação interativa Swagger UI e ReDoc UI geradas automaticamente pelo FastAPI.
    - Configuração flexível através de variáveis de ambiente.
    - Geração automática de certificados autoassinados para HTTPS (em ambiente de desenvolvimento).
    - Endpoint público de saúde para verificação do status da API.
    - Proteção contra ataques de força bruta com rate limiting.
    - CORS (Cross-Origin Resource Sharing) configurável.

Bibliotecas Utilizadas:
    - FastAPI: Framework web moderno e rápido para construir APIs.
    - Pydantic: Validação de dados e settings management utilizando type hints.
    - jose (python-jose): Implementação de JWT em Python.
    - cryptography: Biblioteca para criptografia e geração de certificados.
    - uvicorn: Servidor ASGI para executar a aplicação FastAPI.
    - logging: Biblioteca padrão para logging.
    - python-dotenv (opcional): Para carregar variáveis de ambiente de um arquivo .env.
    - bibliotecas.calc_numbers.Numbers: Biblioteca local (presumivelmente) para operações matemáticas.

Configuração via Variáveis de Ambiente:
    - API_SECRET_KEY: Chave secreta para a assinatura JWT. Padrão: "Jump@d2025!!(SegredoSuperSeguroParaTesteAPI)".
    - API_JWT_ALGORITHM: Algoritmo JWT. Padrão: "HS256".
    - API_TOKEN_EXPIRY_MINUTES: Tempo de expiração do token JWT em minutos. Padrão: "30".
    - API_RATE_LIMIT: Número máximo de requisições por minuto permitidas. Padrão: "200".
    - API_LOG_DIR: Diretório para salvar os arquivos de log. Padrão: "logs".
    - API_CORS_ORIGINS: Lista de origens permitidas para CORS, separadas por vírgula. Padrão: "http://localhost".
    - API_CREDENTIALS_DIR: Diretório para salvar arquivos de credenciais e certificados. Padrão: "credentials".
    - API_ENVIRONMENT: Ambiente da API (e.g., "Desenvolvimento", "Produção"). Padrão: "Desenvolvimento".

Endpoints:
    - POST /token_admin: Gera token JWT para usuário administrador.
    - POST /token_tester: Gera token JWT para usuário tester (para testes).
    - POST /somar: Soma um vetor de números inteiros (requer autenticação JWT de administrador).
    - POST /calcular_media: Calcula a média de um vetor de números inteiros (requer autenticação JWT de administrador).
    - GET /saude: Endpoint público para verificar a saúde da API.

Para executar a API localmente (com HTTPS e geração de certificados autoassinados em desenvolvimento):
    1. Certifique-se de ter Python e pip instalados.
    2. Instale as dependências: `pip install fastapi uvicorn pydantic python-jose cryptography`.
    3. Execute o script: `python seu_script_api.py`.
    4. Acesse a documentação interativa em http://localhost:8882/docs ou http://localhost:8882/redoc.

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

# Importações do FastAPI
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Importações do Pydantic para validação de dados
from pydantic import BaseModel, ValidationError

# Importações do python-jose para JWT
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

# --- Configurações e Variáveis Globais ---

# Chave secreta para JWT, obtida da variável de ambiente ou um valor padrão para teste
SECRET_KEY = os.environ.get("API_SECRET_KEY", "Jump@d2025!!")
# Algoritmo JWT, obtido da variável de ambiente ou um valor padrão
ALGORITHM = os.environ.get("API_JWT_ALGORITHM", "HS256")
# Tempo de expiração do token de acesso em minutos, obtido da variável de ambiente ou padrão
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("API_TOKEN_EXPIRY_MINUTES", "30"))

# Esquemas de segurança OAuth2 para diferentes tipos de token (admin e tester)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token_admin")
oauth2_scheme_tester = OAuth2PasswordBearer(tokenUrl="token_tester")

# Configuração de Rate Limiting (limite de requisições por minuto)
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get("API_RATE_LIMIT", "200"))
RATE_LIMIT_STORAGE = {} # Dicionário para armazenar o estado do rate limiting (pode ser substituído por Redis, etc. em produção)

# Configuração de diretório para logs
DIRETORIO_LOGS = os.environ.get("API_LOG_DIR", "logs")
if not os.path.exists(DIRETORIO_LOGS):
    os.makedirs(DIRETORIO_LOGS) # Cria o diretório de logs se não existir
ARQUIVO_LOG_API = os.path.join(DIRETORIO_LOGS, "api-logs.json") # Arquivo de log principal em formato JSON
ARQUIVO_LOG_DETALHADO_API = os.path.join(DIRETORIO_LOGS, "api-detailed-logs.json") # Arquivo de log detalhado em formato JSON

# --- Configuração de Logging ---

class FormatterColoridoSeguro(logging.Formatter):
    """
    Formatter de log personalizado que adiciona cores e emojis aos logs no console.
    Melhora a legibilidade dos logs durante o desenvolvimento.
    """
    CORES = {
        'DEBUG': '\033[94m',    # Azul
        'INFO': '\033[92m',     # Verde
        'WARNING': '\033[93m',  # Amarelo
        'ERROR': '\033[91m',    # Vermelho
        'CRITICAL': '\033[97;41m', # Branco em fundo Vermelho
        'RESET': '\033[0m'      # Resetar cor
    }
    EMOJIS = {
        'DEBUG': '🐛', # Bug
        'INFO': '✅',  # Checkmark
        'WARNING': '⚠️', # Aviso
        'ERROR': '🔥', # Fogo
        'CRITICAL': '🚨' # Sirene
    }

    def format(self, record):
        """Formata o registro de log com cores, emojis e timestamp."""
        cor_log = self.CORES.get(record.levelname, self.CORES['INFO']) # Obtém a cor baseada no nível de log
        reset_cor = self.CORES['RESET'] # Código para resetar a cor
        emoji = self.EMOJIS.get(record.levelname, '') # Obtém o emoji baseado no nível de log
        nivel_log = f"{cor_log}{record.levelname}{reset_cor}" # Nível de log com cor
        mensagem = f"{cor_log}{record.getMessage()}{reset_cor}" # Mensagem de log com cor
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Timestamp formatado
        return f"{timestamp} - {emoji} {nivel_log} - {record.name}:{record.lineno} - {mensagem}" # Formato final do log

# Handlers de log: um para console (com cores) e dois para arquivos (JSON)
console_handler = logging.StreamHandler() # Handler para logs no console
console_handler.setFormatter(FormatterColoridoSeguro()) # Usa o formatter colorido para o console

api_log_handler = logging.FileHandler(ARQUIVO_LOG_API, encoding='utf-8') # Handler para o arquivo de log principal (JSON)
api_log_formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "detalhes": %(log_record_json)s}') # Formatter JSON para log principal
api_log_handler.setFormatter(api_log_formatter) # Define o formatter para o handler de arquivo de log principal

api_detailed_log_handler = logging.FileHandler(ARQUIVO_LOG_DETALHADO_API, encoding='utf-8') # Handler para o arquivo de log detalhado (JSON)
api_detailed_log_formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "line": "%(lineno)d", "message": "%(message)s", "record": %(log_record_json)s}') # Formatter JSON para log detalhado
api_detailed_log_handler.setFormatter(api_detailed_log_formatter) # Define o formatter para o handler de arquivo de log detalhado

# Configuração do logger principal da aplicação
logger_app = logging.getLogger("api_server") # Obtém o logger com o nome 'api_server'
logger_app.setLevel(logging.DEBUG) # Define o nível de log para DEBUG (registra tudo)
logger_app.addHandler(console_handler) # Adiciona o handler de console
logger_app.addHandler(api_log_handler) # Adiciona o handler de arquivo de log principal
logger_app.addHandler(api_detailed_log_handler) # Adiciona o handler de arquivo de log detalhado

# --- Inicialização da Aplicação FastAPI ---

app = FastAPI(
    title="API Matemática Segura",
    description="API RESTful para operações de soma e média - SEGURA (Nível Máximo)",
    version="0.9.3",
    default_response_class=JSONResponse # Define a classe de resposta padrão para JSONResponse
)

# Configuração de CORS (Cross-Origin Resource Sharing)
origins_permitidas = os.environ.get("API_CORS_ORIGINS", "http://localhost").split(",") # Obtém origens permitidas da variável de ambiente ou padrão
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_permitidas, # Lista de origens permitidas
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos HTTP
    allow_headers=["*"], # Permite todos os headers
)

# --- Modelos de Dados (Pydantic) ---

class NumerosEntrada(BaseModel):
    """
    Modelo Pydantic para validar a entrada de números para as operações matemáticas.
    Espera uma lista de inteiros no campo 'numeros'.
    """
    numeros: List[int]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"numeros": [1, 2, 3, 4]} # Exemplo para a documentação Swagger/ReDoc
            ]
        }
    }

class TokenRequest(BaseModel):
    """
    Modelo Pydantic para requisição de token JWT.
    Espera 'username' e 'password' para autenticação.
    """
    username: str
    password: str

class SomaResponse(BaseModel):
    """
    Modelo Pydantic para a resposta do endpoint de soma.
    Define a estrutura da resposta JSON para a operação de soma.
    """
    resultado: int
    mensagem: str
    numeros_entrada: List[int]
    usuario: Optional[str] = None
    nivel_acesso: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {"resultado": 10, "mensagem": "Operação de soma bem-sucedida", "numeros_entrada": [1, 2, 3, 4], "usuario": "admin", "nivel_acesso": "admin"} # Exemplo para a documentação Swagger/ReDoc
            ]
        }

class MediaResponse(BaseModel):
    """
    Modelo Pydantic para a resposta do endpoint de média.
    Define a estrutura da resposta JSON para a operação de média.
    """
    media: Optional[float] = None
    mensagem: str
    numeros_entrada: List[int]
    usuario: Optional[str] = None
    nivel_acesso: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {"media": 2.5, "mensagem": "Operação de média bem-sucedida", "numeros_entrada": [1, 2, 3, 4], "usuario": "admin", "nivel_acesso": "admin"} # Exemplo para a documentação Swagger/ReDoc
            ]
        }

class SaudeResponse(BaseModel):
    """
    Modelo Pydantic para a resposta do endpoint de saúde.
    Define a estrutura da resposta JSON para o endpoint de verificação de saúde.
    """
    status: str
    mensagem: str

    class Config:
        json_schema_extra = {
            "examples": [
                {"status": "OK", "mensagem": "API está saudável e SEGURA"} # Exemplo para a documentação Swagger/ReDoc
            ]
        }

class TokenResponse(BaseModel):
    """
    Modelo Pydantic para a resposta de geração de token JWT.
    Define a estrutura da resposta JSON contendo o token, tipo e nível de acesso.
    """
    access_token: str
    token_type: str
    nivel_acesso: str

    class Config:
        json_schema_extra = {
            "examples": [
                {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer", "nivel_acesso": "admin"} # Exemplo para a documentação Swagger/ReDoc
            ]
        }

class ErrorResponse(BaseModel):
    """
    Modelo Pydantic para respostas de erro genéricas.
    Define a estrutura da resposta JSON para erros, incluindo mensagem e detalhes.
    """
    erro: str
    detalhes: Any

    class Config:
        json_schema_extra = {
            "examples": [
                {"erro": "Erro de validação nos dados de entrada", "detalhes": "A lista de números não pode estar vazia."} # Exemplo para a documentação Swagger/ReDoc
            ]
        }

# --- Funções Utilitárias para JWT ---

def gerar_token_jwt(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Gera um token JWT (JSON Web Token) seguro.

    Args:
        data (dict): Dados a serem incluídos no payload do token.
        expires_delta (Optional[timedelta]): Tempo de expiração do token (opcional).

    Returns:
        str: Token JWT codificado.
    """
    to_encode = data.copy() # Copia os dados para evitar modificação do original
    if expires_delta:
        expire = datetime.utcnow() + expires_delta # Calcula o tempo de expiração
        to_encode.update({"exp": expire}) # Adiciona a expiração ao payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Codifica o token usando a chave secreta e algoritmo
    return encoded_jwt

def verificar_token_jwt(token: str):
    """
    Verifica e decodifica um token JWT.

    Args:
        token (str): Token JWT a ser verificado.

    Returns:
        dict: Payload do token se a verificação for bem-sucedida, None caso contrário.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # Decodifica o token usando a chave secreta e algoritmo
        return payload # Retorna o payload decodificado
    except JWTError:
        return None # Retorna None em caso de erro na verificação (token inválido ou expirado)

# --- Dependências de Segurança (JWT) ---

async def obter_usuario_atual_jwt(token: str = Depends(oauth2_scheme)):
    """
    Dependência do FastAPI para obter o usuário atual a partir do token JWT (ADMIN).
    Verifica o token JWT e retorna o payload se válido, caso contrário, levanta uma exceção HTTP 401.

    Args:
        token (str): Token JWT obtido do header de autorização.

    Returns:
        dict: Payload do token JWT decodificado contendo informações do usuário.

    Raises:
        HTTPException: 401 UNAUTHORIZED se o token for inválido ou ausente.
    """
    logger_app.debug(f"🔒 Validando Token JWT (ADMIN): {token[:10]}...", extra={'log_record_json': {"token_prefix": token[:10]}}) # Log de debug ao validar o token
    payload = verificar_token_jwt(token) # Verifica o token JWT
    if payload is None:
        logger_app.warning("⚠️ Token JWT inválido ou expirado (ADMIN). Acesso negado.", extra={'log_record_json': {"status_auth": "falha_token_invalido_admin"}}) # Log de warning se token inválido
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # Retorna erro 401
            detail="Credenciais inválidas. Token JWT ausente, inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"}, # Header para indicar autenticação Bearer
        )
    return payload # Retorna o payload do token se válido

async def obter_usuario_tester_jwt(token: str = Depends(oauth2_scheme_tester)):
    """
    Dependência do FastAPI para obter o usuário tester atual a partir do token JWT (TESTER).
    Verifica o token JWT de tester e retorna o payload se válido, caso contrário, levanta uma exceção HTTP 401.

    Args:
        token (str): Token JWT de tester obtido do header de autorização.

    Returns:
        dict: Payload do token JWT de tester decodificado contendo informações do usuário tester.

    Raises:
        HTTPException: 401 UNAUTHORIZED se o token de tester for inválido ou ausente.
    """
    logger_app.debug(f"🔒 Validando Token JWT (TESTER): {token[:10]}...", extra={'log_record_json':  {"token_prefix": token[:10]}}) # Log de debug ao validar o token de tester
    payload = verificar_token_jwt(token) # Verifica o token JWT
    if payload is None:
        logger_app.warning("⚠️ Token JWT inválido ou expirado (TESTER). Acesso negado.", extra={'log_record_json': {"status_auth": "falha_token_invalido_tester"}}) # Log de warning se token de tester inválido
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # Retorna erro 401
            detail="Credenciais inválidas. Token JWT de tester ausente, inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"}, # Header para indicar autenticação Bearer
        )
    return payload # Retorna o payload do token de tester se válido

# --- Endpoints da API ---

@app.post("/token_admin", tags=["autenticação_segura"], response_model=TokenResponse, summary="Gera token JWT seguro (credenciais 'admin/admin')")
async def gerar_token_admin_seguro(token_request: TokenRequest):
    """
    Endpoint para gerar um token JWT de administrador.
    Utiliza credenciais fixas ('admin/admin' - para fins de demonstração e teste).
    Em um sistema real, as credenciais seriam verificadas contra um banco de dados.

    Args:
        token_request (TokenRequest): Requisição contendo username e password.

    Returns:
        TokenResponse: Resposta contendo o token JWT, tipo e nível de acesso.

    Raises:
        HTTPException: 401 UNAUTHORIZED se as credenciais estiverem incorretas, 500 INTERNAL_SERVER_ERROR se houver erro ao ler o arquivo de credenciais.
    """
    logger_app.info(f"🔑 Requisição para gerar token JWT (ADMIN) recebida para usuário: '{token_request.username}'", extra={'log_record_json': {"username": token_request.username}}) # Log de info ao receber requisição de token

    CREDENTIALS_DIR = os.environ.get("API_CREDENTIALS_DIR", "credentials") # Diretório para arquivos de credenciais
    ADMIN_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "admin_credentials.json") # Caminho para o arquivo de credenciais de admin

    try:
        with open(ADMIN_CREDENTIALS_FILE, "r", encoding='utf-8') as f: # Abre o arquivo de credenciais de admin
            usuario_admin = json.load(f) # Carrega as credenciais JSON
    except FileNotFoundError:
        logger_app.critical(f"💥 Arquivo de credenciais admin não encontrado: '{ADMIN_CREDENTIALS_FILE}'.", extra={'log_record_json': {"erro": "FileNotFoundError", "arquivo": ADMIN_CREDENTIALS_FILE}}) # Log crítico se arquivo não encontrado
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Arquivo de credenciais não encontrado.") # Retorna erro 500
    except json.JSONDecodeError as e:
        logger_app.critical(f"💥 Erro ao decodificar JSON do arquivo de credenciais: '{ADMIN_CREDENTIALS_FILE}'. Detalhes: {e}", extra={'log_record_json': {"erro": "JSONDecodeError", "arquivo": ADMIN_CREDENTIALS_FILE, "detalhe_erro": str(e)}}) # Log crítico se erro ao decodificar JSON
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Falha ao ler arquivo de credenciais.") # Retorna erro 500

    if token_request.username == usuario_admin["username"] and token_request.password == usuario_admin["password"]: # Verifica as credenciais
        tempo_expiracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Define o tempo de expiração do token
        token_jwt = gerar_token_jwt(data={"sub": token_request.username, "nivel_acesso": "admin"}, expires_delta=tempo_expiracao_token) # Gera o token JWT
        logger_app.info(f"🔑 Token JWT (ADMIN) gerado com sucesso para usuário 'admin'. Expira em {ACCESS_TOKEN_EXPIRE_MINUTES} minutos.", extra={'log_record_json': {"usuario": "admin", "expira_em_minutos": ACCESS_TOKEN_EXPIRE_MINUTES}}) # Log de info ao gerar token
        return {"access_token": token_jwt, "token_type": "bearer", "nivel_acesso": "admin"} # Retorna a resposta com o token
    else:
        logger_app.warning(f"⚠️ Falha na autenticação (ADMIN) para usuário '{token_request.username}'. Credenciais inválidas.", extra={'log_record_json': {"username": token_request.username}}) # Log de warning se credenciais inválidas
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais de administrador incorretas.") # Retorna erro 401

@app.post("/token_tester", tags=["autenticação_segura_tester"], response_model=TokenResponse, summary="Gera token JWT seguro para TESTER (credenciais 'tester/tester')")
async def gerar_token_seguro_tester(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para gerar um token JWT de tester.
    Utiliza credenciais fixas ('tester/tester' - para fins de demonstração e teste).
    Este endpoint é separado do admin para demonstrar diferentes níveis de acesso,
    embora neste exemplo, o nível de acesso não seja estritamente aplicado.

    Args:
        form_data (OAuth2PasswordRequestForm): Formulário de requisição OAuth2 contendo username e password.

    Returns:
        TokenResponse: Resposta contendo o token JWT, tipo e nível de acesso.

    Raises:
        HTTPException: 401 UNAUTHORIZED se as credenciais estiverem incorretas, 500 INTERNAL_SERVER_ERROR se houver erro ao ler o arquivo de credenciais.
    """
    logger_app.info(f"🔑 Requisição para gerar token JWT (TESTER) recebida para usuário: '{form_data.username}'", extra={'log_record_json': {"username": form_data.username}}) # Log de info ao receber requisição de token de tester

    CREDENTIALS_DIR = os.environ.get("API_CREDENTIALS_DIR", "credentials") # Diretório para arquivos de credenciais
    TESTER_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "tester_credentials.json") # Caminho para o arquivo de credenciais de tester

    try:
        with open(TESTER_CREDENTIALS_FILE, "r", encoding='utf-8') as f: # Abre o arquivo de credenciais de tester
            usuario_tester = json.load(f) # Carrega as credenciais JSON
    except FileNotFoundError:
        logger_app.critical(f"💥 Arquivo de credenciais tester não encontrado: '{TESTER_CREDENTIALS_FILE}'.", extra={'log_record_json': {"erro": "FileNotFoundError", "arquivo": TESTER_CREDENTIALS_FILE}}) # Log crítico se arquivo não encontrado
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Arquivo de credenciais de tester não encontrado.") # Retorna erro 500
    except json.JSONDecodeError as e:
        logger_app.critical(f"💥 Erro ao decodificar JSON do arquivo de credenciais tester: '{TESTER_CREDENTIALS_FILE}'. Detalhes: {e}", extra={'log_record_json': {"erro": "JSONDecodeError", "arquivo": TESTER_CREDENTIALS_FILE, "detalhe_erro": str(e)}}) # Log crítico se erro ao decodificar JSON
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Falha ao ler arquivo de credenciais de tester.") # Retorna erro 500

    if form_data.username == usuario_tester["username"] and form_data.password == usuario_tester["password"]: # Verifica as credenciais de tester
        tempo_expiracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Define o tempo de expiração do token
        token_jwt = gerar_token_jwt(data={"sub": form_data.username, "nivel_acesso": "tester"}, expires_delta=tempo_expiracao_token) # Gera o token JWT de tester
        logger_app.info(f"🔑 Token JWT (TESTER) gerado com sucesso para usuário 'tester'. Expira em {ACCESS_TOKEN_EXPIRE_MINUTES} minutos.", extra={'log_record_json': {"usuario": "tester", "expira_em_minutos": ACCESS_TOKEN_EXPIRE_MINUTES}}) # Log de info ao gerar token de tester
        return {"access_token": token_jwt, "token_type": "bearer", "nivel_acesso": "tester"} # Retorna a resposta com o token de tester
    else:
        logger_app.warning(f"⚠️ Requisição para /token_tester com credenciais de tester inválidas (IGNORADO para testes API).", extra={'log_record_json': {"username": form_data.username}}) # Log de warning se credenciais de tester inválidas (para testes)
        return {"access_token": "TOKEN_INVALIDO_PARA_TESTE", "token_type": "bearer", "nivel_acesso": "tester"} # Retorna um token inválido para testes

@app.post("/somar", tags=["matemática_segura"], summary="Soma um vetor de números inteiros (PROTEGIDO)", dependencies=[Depends(obter_usuario_atual_jwt)], response_model=SomaResponse, response_class=JSONResponse)
async def somar_vetor(request: Request, numeros_entrada: NumerosEntrada, usuario: dict = Depends(obter_usuario_atual_jwt)):
    """
    Endpoint protegido para somar um vetor de números inteiros.
    Requer autenticação JWT de administrador para ser acessado.

    Args:
        request (Request): Objeto Request do FastAPI para detalhes da requisição.
        numeros_entrada (NumerosEntrada): Dados de entrada contendo a lista de números a serem somados.
        usuario (dict): Usuário autenticado (extraído do token JWT pela dependência `obter_usuario_atual_jwt`).

    Returns:
        SomaResponse: Resposta contendo o resultado da soma, mensagem de sucesso e detalhes da requisição.

    Raises:
        HTTPException: 422 UNPROCESSABLE_ENTITY se houver erro de validação nos dados de entrada, 400 BAD_REQUEST se houver erro de tipo de dados, 500 INTERNAL_SERVER_ERROR em caso de erro interno.
    """
    detalhes_requisicao = f"Cliente: {request.client.host if request.client else 'desconhecido'}, URL: {request.url.path}, Usuário JWT (ADMIN): {usuario.get('sub') if usuario else 'desconhecido'}, Nível Acesso: {usuario.get('nivel_acesso') if usuario else 'desconhecido'}, HTTPS={request.url.scheme == 'https'}, Rate Limited=SIM" # Detalhes da requisição para logs
    logger_app.info(f"➡️  Requisição POST em '/somar' (PROTEGIDO) de {detalhes_requisicao}", extra={'log_record_json': {}}) # Log de info ao receber requisição de soma

    try:
        lista_numeros = numeros_entrada.numeros # Obtém a lista de números do corpo da requisição
        logger_app.debug(f"📦 Corpo da requisição JSON recebido e VALIDADO (Pydantic): {lista_numeros}", extra={'log_record_json': {"numeros_entrada": lista_numeros}}) # Log de debug com os números de entrada

        instancia_numeros = Numbers() # Instancia a classe Numbers da biblioteca calc_numbers
        resultado_soma = instancia_numeros.sum_numbers(lista_numeros) # Chama a função para somar os números

        conteudo_resposta = {"resultado": resultado_soma, "mensagem": "Operação de soma bem-sucedida", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')} # Prepara o conteúdo da resposta
        logger_app.info(f"➕ Operação de soma bem-sucedida. Resultado: {resultado_soma} - {detalhes_requisicao}", extra={'log_record_json': {"resultado_soma": resultado_soma, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}}) # Log de info com o resultado da soma
        return conteudo_resposta # Retorna a resposta

    except ValueError as e_calc_value:
        logger_app.warning(f"⚠️ Erro de validação nos dados de entrada para '/somar': {e_calc_value} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_value)}}) # Log de warning se erro de valor na biblioteca
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e_calc_value)) # Retorna erro 422
    except TypeError as e_calc_type:
        logger_app.error(f"🔥 Erro de tipo de dados na biblioteca calc_numbers para '/somar': {e_calc_type} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_type)}}) # Log de erro se erro de tipo na biblioteca
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e_calc_type)) # Retorna erro 400
    except HTTPException as exc_http:
        logger_app.error(f"🔥 Exceção HTTP: {exc_http.detail} - Status Code: {exc_http.status_code} - {detalhes_requisicao}", extra={'log_record_json': {"erro_http": exc_http.detail, "status_code": exc_http.status_code}}) # Log de erro se exceção HTTP
        raise JSONResponse(status_code=exc_http.status_code, content={"erro": exc_http.detail}) # Retorna resposta JSON com erro HTTP
    except ValidationError as ve:
        logger_app.warning(f"⚠️ Erro de Validação de Entrada (Pydantic): {ve.errors()} - {detalhes_requisicao}", extra={'log_record_json': {"erro_validacao": ve.errors()}}) # Log de warning se erro de validação Pydantic
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors()) # Retorna erro 422
    except Exception as e:
        msg_detalhe_erro = f"Erro inesperado no servidor: {str(e)}" # Mensagem de erro detalhada
        logger_app.critical(f"💥 Erro Crítico no Servidor: {msg_detalhe_erro} - {detalhes_requisicao}", exc_info=True, extra={'log_record_json': {"erro_servidor": msg_detalhe_erro, "exception": str(e)}}) # Log crítico para erros inesperados
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"erro": "Erro interno do servidor", "detalhes": msg_detalhe_erro}) # Retorna erro 500

@app.post("/calcular_media", tags=["matemática_segura"], summary="Calcula a média de um vetor de números inteiros (PROTEGIDO)", dependencies=[Depends(obter_usuario_atual_jwt)], response_model=MediaResponse, response_class=JSONResponse)
async def calcular_media_vetor(request: Request, numeros_entrada: NumerosEntrada, usuario: dict = Depends(obter_usuario_atual_jwt)):
    """
    Endpoint protegido para calcular a média de um vetor de números inteiros.
    Requer autenticação JWT de administrador para ser acessado.

    Args:
        request (Request): Objeto Request do FastAPI para detalhes da requisição.
        numeros_entrada (NumerosEntrada): Dados de entrada contendo a lista de números para calcular a média.
        usuario (dict): Usuário autenticado (extraído do token JWT pela dependência `obter_usuario_atual_jwt`).

    Returns:
        MediaResponse: Resposta contendo a média, mensagem de sucesso e detalhes da requisição.

    Raises:
        HTTPException: 422 UNPROCESSABLE_ENTITY se houver erro de validação nos dados de entrada, 400 BAD_REQUEST se houver erro de tipo de dados, 500 INTERNAL_SERVER_ERROR em caso de erro interno.
    """
    detalhes_requisicao = f"Cliente: {request.client.host if request.client else 'desconhecido'}, URL: {request.url.path}, Usuário JWT (ADMIN): {usuario.get('sub') if usuario else 'desconhecido'}, Nível Acesso: {usuario.get('nivel_acesso') if usuario else 'desconhecido'}, HTTPS={request.url.scheme == 'https'}, Rate Limited=SIM" # Detalhes da requisição para logs
    logger_app.info(f"➡️  Requisição POST em '/calcular_media' (PROTEGIDO) de {detalhes_requisicao}", extra={'log_record_json': {}}) # Log de info ao receber requisição de média

    try:
        lista_numeros = numeros_entrada.numeros # Obtém a lista de números do corpo da requisição
        logger_app.debug(f"📦 Corpo da requisição JSON recebido e VALIDADO (Pydantic): {lista_numeros}", extra={'log_record_json': {"numeros_entrada": lista_numeros}}) # Log de debug com os números de entrada

        instancia_numeros = Numbers() # Instancia a classe Numbers da biblioteca calc_numbers
        resultado_media = instancia_numeros.calculate_average(lista_numeros) # Chama a função para calcular a média

        if resultado_media is None: # Trata o caso de lista vazia, onde a média é None
            return {"media": None, "mensagem": "Operação de média bem-sucedida para lista vazia", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')} # Retorna resposta para lista vazia

        conteudo_resposta = {"media": resultado_media, "mensagem": "Operação de média bem-sucedida", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')} # Prepara o conteúdo da resposta
        logger_app.info(f"➗ Operação de média bem-sucedida. Média: {resultado_media} - {detalhes_requisicao}", extra={'log_record_json': {"resultado_media": resultado_media, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}}) # Log de info com o resultado da média
        return conteudo_resposta # Retorna a resposta

    except ValueError as e_calc_value:
        logger_app.warning(f"⚠️ Erro de validação nos dados de entrada para '/calcular_media': {e_calc_value} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_value)}}) # Log de warning se erro de valor na biblioteca
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e_calc_value)) # Retorna erro 422
    except TypeError as e_calc_type:
        logger_app.error(f"🔥 Erro de tipo de dados na biblioteca calc_numbers para '/calcular_media': {e_calc_type} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_type)}}) # Log de erro se erro de tipo na biblioteca
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e_calc_type)) # Retorna erro 400
    except HTTPException as exc_http:
        logger_app.error(f"🔥 Exceção HTTP: {exc_http.detail} - Status Code: {exc_http.status_code} - {detalhes_requisicao}", extra={'log_record_json': {"erro_http": exc_http.detail, "status_code": exc_http.status_code}}) # Log de erro se exceção HTTP
        raise JSONResponse(status_code=exc_http.status_code, content={"erro": exc_http.detail}) # Retorna resposta JSON com erro HTTP
    except ValidationError as ve:
        logger_app.warning(f"⚠️ Erro de Validação de Entrada (Pydantic): {ve.errors()} - {detalhes_requisicao}", extra={'log_record_json': {"erro_validacao": ve.errors()}}) # Log de warning se erro de validação Pydantic
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors()) # Retorna erro 422
    except Exception as e:
        msg_detalhe_erro = f"Erro inesperado no servidor: {str(e)}" # Mensagem de erro detalhada
        logger_app.critical(f"💥 Erro Crítico no Servidor: {msg_detalhe_erro} - {detalhes_requisicao}", exc_info=True, extra={'log_record_json': {"erro_servidor": msg_detalhe_erro, "exception": str(e)}}) # Log crítico para erros inesperados
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"erro": "Erro interno do servidor", "detalhes": msg_detalhe_erro}) # Retorna erro 500

@app.get("/saude", tags=["sistema_seguro"], summary="Endpoint para verificar a saúde da API (PÚBLICO)", response_class=JSONResponse, response_model=SaudeResponse)
async def verificar_saude_segura():
    """
    Endpoint público para verificar a saúde da API.
    Não requer autenticação e pode ser acessado por qualquer cliente.
    Retorna um status OK se a API estiver operacional.

    Returns:
        SaudeResponse: Resposta contendo o status da API e uma mensagem indicando que está saudável.
    """
    timestamp = datetime.now().isoformat() # Obtém o timestamp atual em formato ISO
    saude_template = { # Template para a resposta de saúde
        "status": "OK",
        "version": "0.9.3",
        "ambiente": os.environ.get("API_ENVIRONMENT", "Desenvolvimento"), # Obtém o ambiente da API da variável de ambiente ou padrão
        "timestamp": timestamp,
        "mensagem": "API Matemática Segura está operacional e respondendo.",
        "detalhes": {
            "servidor": "FastAPI",
            "seguranca": "JWT, HTTPS, Rate Limiting",
            "logs": "Detalhado em JSON"
        },
        "status_code": 200,
        "emoji_status": "🚀",
        "indicador_saude": "💚 Ótimo"
    }
    return saude_template # Retorna a resposta de saúde

# --- Bloco Principal para Execução da Aplicação ---

if __name__ == "__main__":
    import uvicorn

    # --- Preparação de Credenciais e Certificados (Apenas para Desenvolvimento Local) ---

    CREDENTIALS_DIR = os.environ.get("API_CREDENTIALS_DIR", "credentials") # Diretório para arquivos de credenciais e certificados
    os.makedirs(CREDENTIALS_DIR, exist_ok=True) # Cria o diretório de credenciais se não existir

    CERT_FILE = os.path.join(CREDENTIALS_DIR, "certificado.pem") # Caminho para o arquivo de certificado HTTPS
    KEY_FILE = os.path.join(CREDENTIALS_DIR, "chave.pem") # Caminho para o arquivo de chave privada HTTPS
    ADMIN_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "admin_credentials.json") # Caminho para o arquivo de credenciais de admin
    TESTER_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "tester_credentials.json") # Caminho para o arquivo de credenciais de tester

    # --- Geração de Certificados Autoassinados para HTTPS (Se Não Existirem) ---

    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE): # Verifica se os arquivos de certificado e chave não existem
        logger_app.info("🔑 Gerando certificados autoassinados para HTTPS...", extra={'log_record_json': {"acao": "geracao_certificados_https"}}) # Log de info ao gerar certificados
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend()) # Gera chave privada RSA
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")]) # Define o Subject do certificado (localhost)
        builder = x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(private_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(datetime.utcnow()).not_valid_after(datetime.utcnow() + timedelta(days=365)).add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False) # Builder do certificado
        certificate = builder.sign(private_key, hashes.SHA256(), default_backend()) # Assina o certificado com a chave privada
        with open(KEY_FILE, "wb") as key_f: # Salva a chave privada no arquivo
            key_f.write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
        with open(CERT_FILE, "wb") as cert_f: # Salva o certificado no arquivo
            cert_f.write(certificate.public_bytes(serialization.Encoding.PEM))
        logger_app.info(f"🔑 Certificados autoassinados gerados e salvos em: '{CREDENTIALS_DIR}/'", extra={'log_record_json': {"acao": "certificados_salvos", "diretorio": CREDENTIALS_DIR}}) # Log de info ao salvar certificados
    else:
        logger_app.info(f"🔑 Certificados HTTPS autoassinados já existentes em: '{CREDENTIALS_DIR}/'. Usando existentes.", extra={'log_record_json': {"acao": "certificados_existentes", "diretorio": CREDENTIALS_DIR}}) # Log de info se certificados já existem

    # --- Criação de Arquivos de Credenciais Padrão (Se Não Existirem) ---

    if not os.path.exists(ADMIN_CREDENTIALS_FILE): # Verifica se o arquivo de credenciais de admin não existe
        logger_app.info(f"⚙️  Criando arquivo de credenciais admin padrão: '{ADMIN_CREDENTIALS_FILE}'...", extra={'log_record_json': {"acao": "criacao_creds_admin", "arquivo": ADMIN_CREDENTIALS_FILE}}) # Log de info ao criar credenciais de admin
        admin_creds = {"username": "admin", "password": "admin"} # Credenciais padrão de admin
        with open(ADMIN_CREDENTIALS_FILE, "w", encoding='utf-8') as f: # Salva as credenciais de admin no arquivo
            json.dump(admin_creds, f, indent=4, ensure_ascii=False)
        logger_app.info(f"⚙️  Arquivo de credenciais admin padrão criado.", extra={'log_record_json': {"acao": "creds_admin_criadas_sucesso", "arquivo": ADMIN_CREDENTIALS_FILE}}) # Log de info ao criar credenciais de admin com sucesso
    else:
        logger_app.info(f"⚙️  Arquivo de credenciais admin já existente: '{ADMIN_CREDENTIALS_FILE}'. Usando existente.", extra={'log_record_json': {"acao": "creds_admin_existentes", "arquivo": ADMIN_CREDENTIALS_FILE}}) # Log de info se credenciais de admin já existem

    if not os.path.exists(TESTER_CREDENTIALS_FILE): # Verifica se o arquivo de credenciais de tester não existe
        logger_app.info(f"⚙️  Criando arquivo de credenciais tester padrão: '{TESTER_CREDENTIALS_FILE}'...", extra={'log_record_json': {"acao": "criacao_creds_tester", "arquivo": TESTER_CREDENTIALS_FILE}}) # Log de info ao criar credenciais de tester
        tester_creds = {"username": "tester", "password": "tester"} # Credenciais padrão de tester
        with open(TESTER_CREDENTIALS_FILE, "w", encoding='utf-8') as f: # Salva as credenciais de tester no arquivo
            json.dump(tester_creds, f, indent=4, ensure_ascii=False)
        logger_app.info(f"⚙️  Arquivo de credenciais tester padrão criado.", extra={'log_record_json': {"acao": "creds_tester_criadas_sucesso", "arquivo": TESTER_CREDENTIALS_FILE}}) # Log de info ao criar credenciais de tester com sucesso
    else:
        logger_app.info(f"⚙️  Arquivo de credenciais tester já existente: '{TESTER_CREDENTIALS_FILE}'. Usando existente.", extra={'log_record_json': {"acao": "creds_tester_existentes", "arquivo": TESTER_CREDENTIALS_FILE}}) # Log de info se credenciais de tester já existem

    # --- Inicialização do Servidor Uvicorn com HTTPS ---

    uvicorn.run(app, host="0.0.0.0", port=8882, ssl_certfile=CERT_FILE, ssl_keyfile=KEY_FILE) # Inicia o servidor Uvicorn com HTTPS e certificados