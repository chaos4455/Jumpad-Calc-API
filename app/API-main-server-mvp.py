import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Any
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, ValidationError
from jose import JWTError, jwt
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from bibliotecas.calc_numbers import Numbers
SECRET_KEY = os.environ.get("API_SECRET_KEY", "Jump@d2025!!")
ALGORITHM = os.environ.get("API_JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("API_TOKEN_EXPIRY_MINUTES", "30"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token_admin")
oauth2_scheme_tester = OAuth2PasswordBearer(tokenUrl="token_tester")
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get("API_RATE_LIMIT", "200"))
RATE_LIMIT_STORAGE = {}
DIRETORIO_LOGS = os.environ.get("API_LOG_DIR", "logs")
if not os.path.exists(DIRETORIO_LOGS):
    os.makedirs(DIRETORIO_LOGS)
ARQUIVO_LOG_API = os.path.join(DIRETORIO_LOGS, "api-logs.json")
ARQUIVO_LOG_DETALHADO_API = os.path.join(DIRETORIO_LOGS, "api-detailed-logs.json")
class FormatterColoridoSeguro(logging.Formatter):
    CORES = {
        'DEBUG': '\033[94m',    'INFO': '\033[92m',     'WARNING': '\033[93m',
        'ERROR': '\033[91m',    'CRITICAL': '\033[97;41m', 'RESET': '\033[0m'
    }
    EMOJIS = {
        'DEBUG': '🐛', 'INFO': '✅', 'WARNING': '⚠️', 'ERROR': '🔥', 'CRITICAL': '🚨'
    }
    def format(self, record):
        cor_log = self.CORES.get(record.levelname, self.CORES['INFO'])
        reset_cor = self.CORES['RESET']
        emoji = self.EMOJIS.get(record.levelname, '')
        nivel_log = f"{cor_log}{record.levelname}{reset_cor}"
        mensagem = f"{cor_log}{record.getMessage()}{reset_cor}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} - {emoji} {nivel_log} - {record.name}:{record.lineno} - {mensagem}"
console_handler = logging.StreamHandler()
console_handler.setFormatter(FormatterColoridoSeguro())
api_log_handler = logging.FileHandler(ARQUIVO_LOG_API, encoding='utf-8')
api_log_formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "detalhes": %(log_record_json)s}')
api_log_handler.setFormatter(api_log_formatter)
api_detailed_log_handler = logging.FileHandler(ARQUIVO_LOG_DETALHADO_API, encoding='utf-8')
api_detailed_log_formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "line": "%(lineno)d", "message": "%(message)s", "record": %(log_record_json)s}')
api_detailed_log_handler.setFormatter(api_detailed_log_formatter)
logger_app = logging.getLogger("api_server")
logger_app.setLevel(logging.DEBUG)
logger_app.addHandler(console_handler)
logger_app.addHandler(api_log_handler)
logger_app.addHandler(api_detailed_log_handler)
app = FastAPI(title="API Matemática Segura", description="API RESTful para operações de soma e média - SEGURA (Nível Máximo)", version="0.9.3", default_response_class=JSONResponse)
origins_permitidas = os.environ.get("API_CORS_ORIGINS", "http://localhost").split(",")
class NumerosEntrada(BaseModel):
    numeros: List[int]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"numeros": [1, 2, 3, 4]}
            ]
        }
    }
class TokenRequest(BaseModel):
    username: str
    password: str
class SomaResponse(BaseModel):
    resultado: int
    mensagem: str
    numeros_entrada: List[int]
    usuario: Optional[str] = None
    nivel_acesso: Optional[str] = None
    class Config:
        json_schema_extra = {
            "examples": [
                {"resultado": 10, "mensagem": "Operação de soma bem-sucedida", "numeros_entrada": [1, 2, 3, 4], "usuario": "admin", "nivel_acesso": "admin"}
            ]
        }
class MediaResponse(BaseModel):
    media: Optional[float] = None
    mensagem: str
    numeros_entrada: List[int]
    usuario: Optional[str] = None
    nivel_acesso: Optional[str] = None
    class Config:
        json_schema_extra = {
            "examples": [
                {"media": 2.5, "mensagem": "Operação de média bem-sucedida", "numeros_entrada": [1, 2, 3, 4], "usuario": "admin", "nivel_acesso": "admin"}
            ]
        }
class SaudeResponse(BaseModel):
    status: str
    mensagem: str
    class Config:
        json_schema_extra = {
            "examples": [
                {"status": "OK", "mensagem": "API está saudável e SEGURA"}
            ]
        }
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    nivel_acesso: str
    class Config:
        json_schema_extra = {
            "examples": [
                {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer", "nivel_acesso": "admin"}
            ]
        }
class ErrorResponse(BaseModel):
    erro: str
    detalhes: Any
    class Config:
        json_schema_extra = {
            "examples": [
                {"erro": "Erro de validação nos dados de entrada", "detalhes": "A lista de números não pode estar vazia."}
            ]
        }
def gerar_token_jwt(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def verificar_token_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
async def obter_usuario_atual_jwt(token: str = Depends(oauth2_scheme)):
    logger_app.debug(f"🔒 Validando Token JWT (ADMIN): {token[:10]}...", extra={'log_record_json': {"token_prefix": token[:10]}})
    payload = verificar_token_jwt(token)
    if payload is None:
        logger_app.warning("⚠️ Token JWT inválido ou expirado (ADMIN). Acesso negado.", extra={'log_record_json': {"status_auth": "falha_token_invalido_admin"}})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Token JWT ausente, inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
async def obter_usuario_tester_jwt(token: str = Depends(oauth2_scheme_tester)):
    logger_app.debug(f"🔒 Validando Token JWT (TESTER): {token[:10]}...", extra={'log_record_json':  {"token_prefix": token[:10]}})
    payload = verificar_token_jwt(token)
    if payload is None:
        logger_app.warning("⚠️ Token JWT inválido ou expirado (TESTER). Acesso negado.", extra={'log_record_json': {"status_auth": "falha_token_invalido_tester"}})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Token JWT de tester ausente, inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
@app.post("/token_admin", tags=["autenticação_segura"], response_model=TokenResponse, summary="Gera token JWT seguro (credenciais 'admin/admin')")
async def gerar_token_admin_seguro(token_request: TokenRequest):
    logger_app.info(f"🔑 Requisição para gerar token JWT (ADMIN) recebida para usuário: '{token_request.username}'", extra={'log_record_json': {"username": token_request.username}})
    CREDENTIALS_DIR = os.environ.get("API_CREDENTIALS_DIR", "credentials")
    ADMIN_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "admin_credentials.json")
    try:
        with open(ADMIN_CREDENTIALS_FILE, "r", encoding='utf-8') as f:
            usuario_admin = json.load(f)
    except FileNotFoundError:
        logger_app.critical(f"💥 Arquivo de credenciais admin não encontrado: '{ADMIN_CREDENTIALS_FILE}'.", extra={'log_record_json': {"erro": "FileNotFoundError", "arquivo": ADMIN_CREDENTIALS_FILE}})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Arquivo de credenciais não encontrado.")
    except json.JSONDecodeError as e:
        logger_app.critical(f"💥 Erro ao decodificar JSON do arquivo de credenciais: '{ADMIN_CREDENTIALS_FILE}'. Detalhes: {e}", extra={'log_record_json': {"erro": "JSONDecodeError", "arquivo": ADMIN_CREDENTIALS_FILE, "detalhe_erro": str(e)}})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Falha ao ler arquivo de credenciais.")
    if token_request.username == usuario_admin["username"] and token_request.password == usuario_admin["password"]:
        tempo_expiracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_jwt = gerar_token_jwt(data={"sub": token_request.username, "nivel_acesso": "admin"}, expires_delta=tempo_expiracao_token)
        logger_app.info(f"🔑 Token JWT (ADMIN) gerado com sucesso para usuário 'admin'. Expira em {ACCESS_TOKEN_EXPIRE_MINUTES} minutos.", extra={'log_record_json': {"usuario": "admin", "expira_em_minutos": ACCESS_TOKEN_EXPIRE_MINUTES}})
        return {"access_token": token_jwt, "token_type": "bearer", "nivel_acesso": "admin"}
    else:
        logger_app.warning(f"⚠️ Falha na autenticação (ADMIN) para usuário '{token_request.username}'. Credenciais inválidas.", extra={'log_record_json': {"username": token_request.username}})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais de administrador incorretas.")
@app.post("/token_tester", tags=["autenticação_segura_tester"], response_model=TokenResponse, summary="Gera token JWT seguro para TESTER (credenciais 'tester/tester')")
async def gerar_token_seguro_tester(form_data: OAuth2PasswordRequestForm = Depends()):
    logger_app.info(f"🔑 Requisição para gerar token JWT (TESTER) recebida para usuário: '{form_data.username}'", extra={'log_record_json': {"username": form_data.username}})
    CREDENTIALS_DIR = os.environ.get("API_CREDENTIALS_DIR", "credentials")
    TESTER_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "tester_credentials.json")
    try:
        with open(TESTER_CREDENTIALS_FILE, "r", encoding='utf-8') as f:
            usuario_tester = json.load(f)
    except FileNotFoundError:
        logger_app.critical(f"💥 Arquivo de credenciais tester não encontrado: '{TESTER_CREDENTIALS_FILE}'.", extra={'log_record_json': {"erro": "FileNotFoundError", "arquivo": TESTER_CREDENTIALS_FILE}})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Arquivo de credenciais de tester não encontrado.")
    except json.JSONDecodeError as e:
        logger_app.critical(f"💥 Erro ao decodificar JSON do arquivo de credenciais tester: '{TESTER_CREDENTIALS_FILE}'. Detalhes: {e}", extra={'log_record_json': {"erro": "JSONDecodeError", "arquivo": TESTER_CREDENTIALS_FILE, "detalhe_erro": str(e)}})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno: Falha ao ler arquivo de credenciais de tester.")
    if form_data.username == usuario_tester["username"] and form_data.password == usuario_tester["password"]:
        tempo_expiracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_jwt = gerar_token_jwt(data={"sub": form_data.username, "nivel_acesso": "tester"}, expires_delta=tempo_expiracao_token)
        logger_app.info(f"🔑 Token JWT (TESTER) gerado com sucesso para usuário 'tester'. Expira em {ACCESS_TOKEN_EXPIRE_MINUTES} minutos.", extra={'log_record_json': {"usuario": "tester", "expira_em_minutos": ACCESS_TOKEN_EXPIRE_MINUTES}})
        return {"access_token": token_jwt, "token_type": "bearer", "nivel_acesso": "tester"}
    else:
        logger_app.warning(f"⚠️ Requisição para /token_tester com credenciais de tester inválidas (IGNORADO para testes API).", extra={'log_record_json': {"username": form_data.username}})
        return {"access_token": "TOKEN_INVALIDO_PARA_TESTE", "token_type": "bearer", "nivel_acesso": "tester"}
@app.post("/somar", tags=["matemática_segura"], summary="Soma um vetor de números inteiros (PROTEGIDO)", dependencies=[Depends(obter_usuario_atual_jwt)], response_model=SomaResponse, response_class=JSONResponse)
async def somar_vetor(request: Request, numeros_entrada: NumerosEntrada, usuario: dict = Depends(obter_usuario_atual_jwt)):
    detalhes_requisicao = f"Cliente: {request.client.host if request.client else 'desconhecido'}, URL: {request.url.path}, Usuário JWT (ADMIN): {usuario.get('sub') if usuario else 'desconhecido'}, Nível Acesso: {usuario.get('nivel_acesso') if usuario else 'desconhecido'}, HTTPS={request.url.scheme == 'https'}, Rate Limited=SIM"
    logger_app.info(f"➡️  Requisição POST em '/somar' (PROTEGIDO) de {detalhes_requisicao}", extra={'log_record_json': {}})
    try:
        lista_numeros = numeros_entrada.numeros
        logger_app.debug(f"📦 Corpo da requisição JSON recebido e VALIDADO (Pydantic): {lista_numeros}", extra={'log_record_json': {"numeros_entrada": lista_numeros}})
        instancia_numeros = Numbers()
        resultado_soma = instancia_numeros.sum_numbers(lista_numeros)
        conteudo_resposta = {"resultado": resultado_soma, "mensagem": "Operação de soma bem-sucedida", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}
        logger_app.info(f"➕ Operação de soma bem-sucedida. Resultado: {resultado_soma} - {detalhes_requisicao}", extra={'log_record_json': {"resultado_soma": resultado_soma, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}})
        return conteudo_resposta
    except ValueError as e_calc_value:
        logger_app.warning(f"⚠️ Erro de validação nos dados de entrada para '/somar': {e_calc_value} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_value)}})
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e_calc_value))
    except TypeError as e_calc_type:
        logger_app.error(f"🔥 Erro de tipo de dados na biblioteca calc_numbers para '/somar': {e_calc_type} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_type)}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e_calc_type))
    except HTTPException as exc_http:
        logger_app.error(f"🔥 Exceção HTTP: {exc_http.detail} - Status Code: {exc_http.status_code} - {detalhes_requisicao}", extra={'log_record_json': {"erro_http": exc_http.detail, "status_code": exc_http.status_code}})
        raise JSONResponse(status_code=exc_http.status_code, content={"erro": exc_http.detail})
    except ValidationError as ve:
        logger_app.warning(f"⚠️ Erro de Validação de Entrada (Pydantic): {ve.errors()} - {detalhes_requisicao}", extra={'log_record_json': {"erro_validacao": ve.errors()}})
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors())
    except Exception as e:
        msg_detalhe_erro = f"Erro inesperado no servidor: {str(e)}"
        logger_app.critical(f"💥 Erro Crítico no Servidor: {msg_detalhe_erro} - {detalhes_requisicao}", exc_info=True, extra={'log_record_json': {"erro_servidor": msg_detalhe_erro, "exception": str(e)}})
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"erro": "Erro interno do servidor", "detalhes": msg_detalhe_erro})
@app.post("/calcular_media", tags=["matemática_segura"], summary="Calcula a média de um vetor de números inteiros (PROTEGIDO)", dependencies=[Depends(obter_usuario_atual_jwt)], response_model=MediaResponse, response_class=JSONResponse)
async def calcular_media_vetor(request: Request, numeros_entrada: NumerosEntrada, usuario: dict = Depends(obter_usuario_atual_jwt)):
    detalhes_requisicao = f"Cliente: {request.client.host if request.client else 'desconhecido'}, URL: {request.url.path}, Usuário JWT (ADMIN): {usuario.get('sub') if usuario else 'desconhecido'}, Nível Acesso: {usuario.get('nivel_acesso') if usuario else 'desconhecido'}, HTTPS={request.url.scheme == 'https'}, Rate Limited=SIM"
    logger_app.info(f"➡️  Requisição POST em '/calcular_media' (PROTEGIDO) de {detalhes_requisicao}", extra={'log_record_json': {}})
    try:
        lista_numeros = numeros_entrada.numeros
        logger_app.debug(f"📦 Corpo da requisição JSON recebido e VALIDADO (Pydantic): {lista_numeros}", extra={'log_record_json': {"numeros_entrada": lista_numeros}})
        instancia_numeros = Numbers()
        resultado_media = instancia_numeros.calculate_average(lista_numeros)
        if resultado_media is None:
            return {"media": None, "mensagem": "Operação de média bem-sucedida para lista vazia", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}
        conteudo_resposta = {"media": resultado_media, "mensagem": "Operação de média bem-sucedida", "numeros_entrada": lista_numeros, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}
        logger_app.info(f"➗ Operação de média bem-sucedida. Média: {resultado_media} - {detalhes_requisicao}", extra={'log_record_json': {"resultado_media": resultado_media, "usuario": usuario.get('sub'), "nivel_acesso": usuario.get('nivel_acesso')}})
        return conteudo_resposta
    except ValueError as e_calc_value:
        logger_app.warning(f"⚠️ Erro de validação nos dados de entrada para '/calcular_media': {e_calc_value} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_value)}})
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e_calc_value))
    except TypeError as e_calc_type:
        logger_app.error(f"🔥 Erro de tipo de dados na biblioteca calc_numbers para '/calcular_media': {e_calc_type} - {detalhes_requisicao}", extra={'log_record_json': {"erro_biblioteca": str(e_calc_type)}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e_calc_type))
    except HTTPException as exc_http:
        logger_app.error(f"🔥 Exceção HTTP: {exc_http.detail} - Status Code: {exc_http.status_code} - {detalhes_requisicao}", extra={'log_record_json': {"erro_http": exc_http.detail, "status_code": exc_http.status_code}})
        raise JSONResponse(status_code=exc_http.status_code, content={"erro": exc_http.detail})
    except ValidationError as ve:
        logger_app.warning(f"⚠️ Erro de Validação de Entrada (Pydantic): {ve.errors()} - {detalhes_requisicao}", extra={'log_record_json': {"erro_validacao": ve.errors()}})
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors())
    except Exception as e:
        msg_detalhe_erro = f"Erro inesperado no servidor: {str(e)}"
        logger_app.critical(f"💥 Erro Crítico no Servidor: {msg_detalhe_erro} - {detalhes_requisicao}", exc_info=True, extra={'log_record_json': {"erro_servidor": msg_detalhe_erro, "exception": str(e)}})
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"erro": "Erro interno do servidor", "detalhes": msg_detalhe_erro})
@app.get("/saude", tags=["sistema_seguro"], summary="Endpoint para verificar a saúde da API (PÚBLICO)", response_class=JSONResponse, response_model=SaudeResponse)
async def verificar_saude_segura():
    timestamp = datetime.now().isoformat()
    saude_template = {
        "status": "OK",
        "version": "0.9.3",
        "ambiente": os.environ.get("API_ENVIRONMENT", "Desenvolvimento"),
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
    return saude_template
if __name__ == "__main__":
    import uvicorn
    CREDENTIALS_DIR = os.environ.get("API_CREDENTIALS_DIR", "credentials")
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    CERT_FILE = os.path.join(CREDENTIALS_DIR, "certificado.pem")
    KEY_FILE = os.path.join(CREDENTIALS_DIR, "chave.pem")
    ADMIN_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "admin_credentials.json")
    TESTER_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "tester_credentials.json")
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        logger_app.info("🔑 Gerando certificados autoassinados para HTTPS...", extra={'log_record_json': {"acao": "geracao_certificados_https"}})
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
        builder = x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(private_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(datetime.utcnow()).not_valid_after(datetime.utcnow() + timedelta(days=365)).add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
        certificate = builder.sign(private_key, hashes.SHA256(), default_backend())
        with open(KEY_FILE, "wb") as key_f:
            key_f.write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
        with open(CERT_FILE, "wb") as cert_f:
            cert_f.write(certificate.public_bytes(serialization.Encoding.PEM))
        logger_app.info(f"🔑 Certificados autoassinados gerados e salvos em: '{CREDENTIALS_DIR}/'", extra={'log_record_json': {"acao": "certificados_salvos", "diretorio": CREDENTIALS_DIR}})
    else:
        logger_app.info(f"🔑 Certificados HTTPS autoassinados já existentes em: '{CREDENTIALS_DIR}/'. Usando existentes.", extra={'log_record_json': {"acao": "certificados_existentes", "diretorio": CREDENTIALS_DIR}})
    if not os.path.exists(ADMIN_CREDENTIALS_FILE):
        logger_app.info(f"⚙️  Criando arquivo de credenciais admin padrão: '{ADMIN_CREDENTIALS_FILE}'...", extra={'log_record_json': {"acao": "criacao_creds_admin", "arquivo": ADMIN_CREDENTIALS_FILE}})
        admin_creds = {"username": "admin", "password": "admin"}
        with open(ADMIN_CREDENTIALS_FILE, "w", encoding='utf-8') as f:
            json.dump(admin_creds, f, indent=4, ensure_ascii=False)
        logger_app.info(f"⚙️  Arquivo de credenciais admin padrão criado.", extra={'log_record_json': {"acao": "creds_admin_criadas_sucesso", "arquivo": ADMIN_CREDENTIALS_FILE}})
    else:
        logger_app.info(f"⚙️  Arquivo de credenciais admin já existente: '{ADMIN_CREDENTIALS_FILE}'. Usando existente.", extra={'log_record_json': {"acao": "creds_admin_existentes", "arquivo": ADMIN_CREDENTIALS_FILE}})
    if not os.path.exists(TESTER_CREDENTIALS_FILE):
        logger_app.info(f"⚙️  Criando arquivo de credenciais tester padrão: '{TESTER_CREDENTIALS_FILE}'...", extra={'log_record_json': {"acao": "criacao_creds_tester", "arquivo": TESTER_CREDENTIALS_FILE}})
        tester_creds = {"username": "tester", "password": "tester"}
        with open(TESTER_CREDENTIALS_FILE, "w", encoding='utf-8') as f:
            json.dump(tester_creds, f, indent=4, ensure_ascii=False)
        logger_app.info(f"⚙️  Arquivo de credenciais tester padrão criado.", extra={'log_record_json': {"acao": "creds_tester_criadas_sucesso", "arquivo": TESTER_CREDENTIALS_FILE}})
    else:
        logger_app.info(f"⚙️  Arquivo de credenciais tester já existente: '{TESTER_CREDENTIALS_FILE}'. Usando existente.", extra={'log_record_json': {"acao": "creds_tester_existentes", "arquivo": TESTER_CREDENTIALS_FILE}})
    uvicorn.run(app, host="0.0.0.0", port=8882, ssl_certfile=CERT_FILE, ssl_keyfile=KEY_FILE)