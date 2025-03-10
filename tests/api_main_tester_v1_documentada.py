# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados para API Matemática Segura (Testes de Integração)

Este script Python implementa uma suíte de testes automatizados para verificar a
funcionalidade e robustez da API Matemática Segura, utilizando a biblioteca `unittest`.
Os testes cobrem diversos cenários, incluindo operações de soma e média, validação de
entrada de dados, endpoints protegidos por autenticação JWT, e o endpoint público de saúde.

A suíte de testes inclui:

    - Testes de endpoints públicos e protegidos (requer token JWT de administrador).
    - Validação de respostas da API (status code, corpo da resposta em JSON).
    - Testes de casos de sucesso e de falha (erros de validação, erros de tipo, etc.).
    - Geração de logs detalhados em formato JSON para cada execução de teste.
    - Saída colorida no console para facilitar a leitura dos resultados dos testes.

Configuração:
    - A URL base da API e a verificação de certificado SSL podem ser configuradas através
      de variáveis de ambiente `API_TEST_URL` e `API_VERIFY_SSL`, respectivamente.
    - As credenciais padrão 'admin/admin' são utilizadas para obter o token JWT de administrador.

Para executar os testes, basta executar este script Python diretamente. Os resultados
serão exibidos no console e um arquivo de log detalhado em JSON será gerado no diretório `test_logs`.

Bibliotecas Utilizadas:
    - requests: Para fazer requisições HTTP para a API.
    - json: Para manipulação de dados JSON.
    - os: Para manipulação de arquivos e variáveis de ambiente.
    - unittest: Framework de testes unitários do Python.
    - time: Para medição de tempo de execução dos testes.
    - datetime: Para geração de timestamps nos logs.
    - colorama: Para adicionar cores e estilos à saída do console, facilitando a leitura.

Diretórios e Arquivos Gerados:
    - test_logs/: Diretório para armazenar os arquivos de log dos testes.
        - api-test-log.json: Arquivo de log principal em formato JSON, contendo detalhes de cada execução de teste.

Execução:
    Execute este script diretamente para iniciar a suíte de testes. Os resultados e logs
    serão gerados automaticamente.

Criado por: Elias Andrade
Data de Criação: 10 de Março de 2025
"""
import requests # 🚀 Biblioteca para fazer requisições HTTP
import json # 🗄️ Biblioteca para trabalhar com JSON
import os # 📁 Biblioteca para interagir com o sistema operacional (e.g., variáveis de ambiente, caminhos de arquivos)
import unittest # 🧪 Framework de testes unitários do Python
import time # ⏱️ Biblioteca para funções relacionadas a tempo
from datetime import datetime # 📅 Biblioteca para trabalhar com datas e horas
import colorama # 🎨 Biblioteca para adicionar cores e estilos ao texto no terminal
from colorama import Fore, Back, Style # 🎨 Importa estilos e cores específicos do colorama

colorama.init(autoreset=True) # 🎨 Inicializa o Colorama para que as cores sejam resetadas automaticamente após cada print

API_BASE_URL = os.environ.get("API_TEST_URL", "https://localhost:8882") # 🌐 URL base da API para testes, configurável via variável de ambiente API_TEST_URL
VERIFY_SSL_CERT = os.environ.get("API_VERIFY_SSL", False) == 'True' # 🔒 Define se a verificação do certificado SSL está habilitada, configurável via API_VERIFY_SSL
LOG_DIR = "test_logs" # 🗂️ Diretório para salvar os arquivos de log dos testes
LOG_FILE = os.path.join(LOG_DIR, "api-test-log.json") # 📝 Caminho completo para o arquivo de log JSON

ADMIN_TOKEN = None # 🔑 Variável global para armazenar o token JWT de administrador, inicialmente None

def obter_token_admin():
    """
    Obtém um token JWT de administrador da API para autenticação em endpoints protegidos.

    Utiliza as credenciais padrão 'admin/admin' para solicitar o token no endpoint '/token_admin' da API.
    Se a requisição for bem-sucedida, armazena o token na variável global ADMIN_TOKEN e o retorna.
    Em caso de falha na requisição ou erro HTTP, imprime uma mensagem de erro colorida no console e retorna None.

    Returns:
        str | None: O token JWT de administrador (string) se obtido com sucesso, ou None em caso de falha.
    """
    global ADMIN_TOKEN # 🔑 Indica que a variável global ADMIN_TOKEN será modificada nesta função
    token_url = f"{API_BASE_URL}/token_admin" # 🔗 URL completa para o endpoint de geração de token de admin
    credenciais = {"username": "admin", "password": "admin"} # 👤 Credenciais padrão para o usuário administrador
    try:
        resposta = requests.post(token_url, json=credenciais, verify=VERIFY_SSL_CERT) # 📧 Faz a requisição POST para obter o token, enviando as credenciais em JSON
        resposta.raise_for_status() # 🚨 Levanta uma exceção para status codes de erro (e.g., 4xx, 5xx)
        ADMIN_TOKEN = resposta.json().get("access_token") # 🔑 Extrai o token de acesso do JSON da resposta e armazena na variável global
        return ADMIN_TOKEN # 🔑 Retorna o token JWT obtido
    except requests.exceptions.RequestException as e: # ❗ Captura exceções de requisição (e.g., falha de conexão, timeout, erro HTTP)
        print(Fore.RED + Style.BRIGHT + f"🔥 Erro ao obter token ADMIN: {e}" + Style.RESET_ALL) # 🔴 Imprime mensagem de erro colorida no console
        return None # ❌ Retorna None para indicar que não foi possível obter o token

def colored_print_success(msg):
    """Imprime uma mensagem no console com formatação de sucesso (verde e negrito)."""
    print(Fore.GREEN + Style.BRIGHT + "✅ " + msg + Style.RESET_ALL) # ✅ Imprime a mensagem em verde e negrito

def colored_print_failure(msg):
    """Imprime uma mensagem no console com formatação de falha (vermelho e negrito)."""
    print(Fore.RED + Style.BRIGHT + "❌ " + msg + Style.RESET_ALL) # ❌ Imprime a mensagem em vermelho e negrito

def colored_print_info(msg):
    """Imprime uma mensagem no console com formatação de informação (ciano e negrito)."""
    print(Fore.CYAN + Style.BRIGHT + "ℹ️  " + msg + Style.RESET_ALL) # ℹ️ Imprime a mensagem em ciano e negrito

def colored_print_warning(msg):
    """Imprime uma mensagem no console com formatação de aviso (amarelo e negrito)."""
    print(Fore.YELLOW + Style.BRIGHT + "⚠️  " + msg + Style.RESET_ALL) # ⚠️ Imprime a mensagem em amarelo e negrito

def colored_print_header(msg):
    """Imprime um cabeçalho formatado no console (fundo azul, texto branco e negrito)."""
    print(Back.BLUE + Fore.WHITE + Style.BRIGHT + " " + msg + " " + Style.RESET_ALL) # 🔵 Imprime um cabeçalho com fundo azul, texto branco e negrito

class ApiTests(unittest.TestCase):
    """
    Classe que define a suíte de testes para a API Matemática Segura.

    Herda de `unittest.TestCase` e contém métodos de teste para diferentes endpoints da API,
    incluindo testes de sucesso, falha e validação de dados. Utiliza tokens JWT para testar
    endpoints protegidos e gera logs detalhados de cada teste executado.

    Métodos:
        setUp(): Configuração inicial para cada teste, obtendo token JWT e definindo headers.
        tearDown(): Limpeza após cada teste, salvando logs e calculando a duração do teste.
        _start_test_logging(test_name): Inicia o logging para um caso de teste específico.
        _log_request_response(method, url, headers, data, response): Loga detalhes de requisição e resposta HTTP.
        _save_log_to_file(): Salva as entradas de log acumuladas em um arquivo JSON.
        _testar_rota_post(url_path, token_headers, data, expected_status, expected_result_key, expected_result_value, test_name):
            Método genérico para testar rotas POST, validando status code e conteúdo da resposta.
        test_rota_saude(): Testa o endpoint público '/saude'.
        test_rota_somar_numeros_positivos(): Testa o endpoint '/somar' com números positivos válidos.
        test_rota_calcular_media_numeros_positivos(): Testa o endpoint '/calcular_media' com números positivos válidos.
        test_rota_somar_lista_vazia_erro_422(): Testa o endpoint '/somar' com lista vazia, esperando erro 422.
        test_rota_calcular_media_lista_vazia_retorna_none(): Testa o endpoint '/calcular_media' com lista vazia, esperando média None.
        ... (outros métodos de teste para diferentes cenários e validações)
    """

    def setUp(self):
        """
        Configuração inicial executada antes de cada método de teste.

        Obtém o token JWT de administrador se ainda não estiver definido globalmente.
        Se o token não for obtido, o teste é pulado (skipTest). Define os headers de
        autorização com o token JWT para as requisições aos endpoints protegidos.
        Inicializa a lista de entradas de log para cada teste (`self.log_entries`).
        """
        global ADMIN_TOKEN # 🔑 Indica que a variável global ADMIN_TOKEN será acessada
        if not ADMIN_TOKEN: # ✅ Verifica se o token ADMIN já foi obtido
            ADMIN_TOKEN = obter_token_admin() # 🔑 Obtém o token ADMIN chamando a função obter_token_admin()
            if not ADMIN_TOKEN: # ❌ Se não foi possível obter o token ADMIN
                self.skipTest("Token ADMIN não obtido, pulando testes protegidos.") # 🚫 Pula todos os testes na classe ApiTests se o token ADMIN não for obtido
        self.admin_token = ADMIN_TOKEN # 🔑 Armazena o token ADMIN na variável de instância para uso nos testes
        self.headers_admin = {"Authorization": f"Bearer {self.admin_token}"} # 🛡️ Define os headers de autorização com o token JWT para endpoints protegidos
        self.log_entries = [] # 📝 Inicializa a lista para armazenar as entradas de log dos testes

    def tearDown(self):
        """
        Executado após cada método de teste para realizar a limpeza e logging.

        Calcula a duração do teste, determina o status (PASSOU/FALHOU) baseado em erros e falhas,
        cria uma entrada de log com os resultados do teste e salva essa entrada no arquivo de log JSON.
        Limpa a lista de entradas de log para o próximo teste.
        """
        end_time = time.time() # ⏱️ Marca o tempo de fim do teste
        test_duration = end_time - self.start_test_time # ⏱️ Calcula a duração do teste em segundos
        status = "PASSOU" if not self._outcome.errors and not self._outcome.failures else "FALHOU" # ✅/❌ Determina o status do teste baseado em erros e falhas

        log_entry = { # 📝 Cria uma entrada de log para o teste atual
            "test_name": self._testMethodName, # 🏷️ Nome do método de teste executado
            "status": status, # ✅/❌ Status do teste (PASSOU ou FALHOU)
            "duration_seconds": f"{test_duration:.4f}", # ⏱️ Duração do teste formatada em segundos
            "timestamp": datetime.now().isoformat(), # 📅 Timestamp da finalização do teste em formato ISO
            "details": self.current_test_log # ℹ️ Logs detalhados da requisição e resposta para este teste
        }
        self.log_entries.append(log_entry) # 📝 Adiciona a entrada de log à lista de logs
        self._save_log_to_file() # 💾 Salva os logs acumulados no arquivo

    def _start_test_logging(self, test_name):
        """Inicia o logging para um novo caso de teste, preparando para armazenar os logs."""
        self.current_test_log = [] # 📝 Inicializa a lista para armazenar os logs do teste atual
        self.start_test_time = time.time() # ⏱️ Marca o tempo de início do teste

    def _log_request_response(self, method, url, headers, data, response):
        """
        Loga os detalhes de uma requisição e sua resposta para o log do teste atual.

        Armazena informações como método HTTP, URL, headers da requisição, dados enviados (se houver),
        status code da resposta, headers da resposta e o corpo da resposta (texto).

        Args:
            method (str): Método HTTP da requisição (e.g., 'GET', 'POST').
            url (str): URL da requisição.
            headers (dict): Headers da requisição.
            data (dict | None): Dados enviados no corpo da requisição (para métodos como POST). Pode ser None.
            response (requests.Response): Objeto de resposta da requisição HTTP.
        """
        log_data = { # 📝 Cria um dicionário para armazenar os dados da requisição e resposta
            "request": { # ➡️ Dados da requisição
                "method": method, # ⚙️ Método HTTP (GET, POST, etc.)
                "url": url, # 🔗 URL da requisição
                "headers": headers, # ⚙️ Headers da requisição
                "data": data if method == 'POST' else None, # 📦 Dados enviados (se for requisição POST)
                "json": data if method == 'POST' else None # 📦 Dados enviados como JSON (se for requisição POST)
            },
            "response": { # ⬅️ Dados da resposta
                "status_code": response.status_code, # 🔢 Status code HTTP da resposta
                "headers": dict(response.headers), # ⚙️ Headers da resposta (convertidos para dict para serialização JSON)
                "body": response.text # 📄 Corpo da resposta como texto
            }
        }
        self.current_test_log.append(log_data) # 📝 Adiciona os dados de log à lista de logs do teste atual

    def _save_log_to_file(self):
        """
        Salva as entradas de log acumuladas (de todos os testes executados) em um arquivo JSON.

        Verifica se o diretório de logs existe e o cria se necessário. Adiciona um cabeçalho ao log
        com o timestamp da execução dos testes e o nome da suíte de testes. Formata as entradas de log
        em JSON e as escreve no arquivo, garantindo que seja um JSON válido mesmo com múltiplas execuções.
        Limpa a lista de entradas de log após salvar no arquivo.
        """
        if not os.path.exists(LOG_DIR): # 📁 Verifica se o diretório de logs existe
            os.makedirs(LOG_DIR) # 📁 Cria o diretório de logs se não existir
        log_header = {"test_run_timestamp": datetime.now().isoformat(), "test_suite": "ApiTests"} # 📝 Cabeçalho do log com timestamp e nome da suíte

        try:
            file_exists = os.path.exists(LOG_FILE) # ✅ Verifica se o arquivo de log já existe
            with open(LOG_FILE, 'a') as f: # 📝 Abre o arquivo de log em modo de append ('a')
                if not file_exists: # 🆕 Se o arquivo não existia, inicia o JSON com o cabeçalho 'test_runs'
                    f.write('{"test_runs": [\n') # 📝 Início da estrutura JSON 'test_runs'
                else: # ➕ Se o arquivo já existia, adiciona uma vírgula para separar a execução anterior
                    f.write(',\n') # 📝 Adiciona vírgula para separar as execuções no array 'test_runs'

                json.dump(log_header, f, indent=4, ensure_ascii=False) # 📝 Escreve o cabeçalho do log em JSON formatado
                f.write(',\n"tests": [\n') # 📝 Início do array 'tests' dentro de cada 'test_run'

                for i, entry in enumerate(self.log_entries): # 📝 Itera sobre cada entrada de log na lista
                    json.dump(entry, f, indent=4, ensure_ascii=False) # 📝 Escreve a entrada de log em JSON formatado
                    if i < len(self.log_entries) - 1: # ➕ Adiciona vírgula se não for a última entrada para separar os testes
                        f.write(',') # 📝 Adiciona vírgula entre as entradas de teste no array 'tests'
                    f.write('\n') # 📝 Nova linha para formatação

                f.write(']\n}') # 📝 Fecha o array 'tests' e o objeto 'test_runs'
                self.log_entries = [] # 📝 Limpa a lista de entradas de log após salvar no arquivo

        except Exception as e: # ❗ Captura exceções que podem ocorrer ao salvar o log
            colored_print_failure(f"❌ Erro ao salvar log em '{LOG_FILE}': {e}") # ❌ Imprime mensagem de erro no console se falhar ao salvar o log

    def _testar_rota_post(self, url_path, token_headers, data, expected_status=200, expected_result_key=None, expected_result_value=None, test_name="Rota POST"):
        """
        Método genérico para testar endpoints POST da API, validando status code e corpo da resposta.

        Faz uma requisição POST para a URL especificada, com headers e dados fornecidos.
        Verifica se o status code da resposta corresponde ao esperado. Se um `expected_result_key`
        for fornecido, tenta validar se a chave existe na resposta JSON e, opcionalmente, se o valor
        associado a essa chave corresponde a `expected_result_value`. Em caso de falha em qualquer
        validação, imprime mensagens de erro coloridas no console e registra a falha no teste.

        Args:
            url_path (str): Caminho da URL do endpoint a ser testado (relativo à URL base da API).
            token_headers (dict): Headers HTTP a serem incluídos na requisição, geralmente contendo o token JWT.
            data (dict): Dados a serem enviados no corpo da requisição POST (em formato JSON).
            expected_status (int, optional): Status code HTTP esperado na resposta. Padrão: 200.
            expected_result_key (str, optional): Chave esperada no JSON da resposta para validação do valor. Padrão: None.
            expected_result_value (any, optional): Valor esperado para a chave `expected_result_key` no JSON da resposta. Padrão: None.
            test_name (str, optional): Nome descritivo para o teste, usado nas mensagens de log e console. Padrão: "Rota POST".

        Returns:
            requests.Response: O objeto de resposta da requisição HTTP para inspeção adicional, se necessário.
        """
        url = f"{API_BASE_URL}{url_path}" # 🔗 Constrói a URL completa do endpoint
        self._start_test_logging(test_name) # 📝 Inicia o logging para este teste

        resposta = requests.post(url, headers=token_headers, json=data, verify=VERIFY_SSL_CERT) # 📧 Faz a requisição POST para o endpoint
        self._log_request_response('POST', url, token_headers, data, resposta) # 📝 Loga os detalhes da requisição e resposta

        if resposta.status_code != expected_status: # ❌ Verifica se o status code da resposta é o esperado
            colored_print_failure(f"❌ {test_name} FALHOU: Status code incorreto. Esperado: {expected_status}, Obtido: {resposta.status_code}. Response Body: {resposta.text}") # 🔴 Imprime mensagem de falha no console
            self.assertEqual(resposta.status_code, expected_status) # 🚨 Falha no teste se o status code estiver incorreto
            return # 🛑 Retorna imediatamente em caso de falha no status code

        if expected_status < 400 and expected_result_key: # ✅ Se o status code for de sucesso (2xx, 3xx) e uma chave de resultado esperada for fornecida
            try:
                response_json = resposta.json() # 🗄️ Tenta decodificar o corpo da resposta como JSON
                actual_value = response_json.get(expected_result_key) # 🔑 Obtém o valor da chave esperada do JSON da resposta
                if expected_result_value is not None: # ✅ Se um valor de resultado esperado específico for fornecido
                    if actual_value == expected_result_value: # ✅ Verifica se o valor obtido corresponde ao valor esperado
                        colored_print_success(f"✅ {test_name} OK: Valor de '{expected_result_key}' validado. ({expected_result_value})") # 🟢 Imprime mensagem de sucesso no console
                    else: # ❌ Se o valor obtido não corresponder ao valor esperado
                        colored_print_failure(f"❌ {test_name} FALHOU: Valor incorreto para chave '{expected_result_key}'. Esperado: {expected_result_value}, Obtido: {actual_value}. Response: {response_json}") # 🔴 Imprime mensagem de falha no console
                        self.fail(f"Valor incorreto para chave '{expected_result_key}'. Esperado: {expected_result_value}, Obtido: {actual_value}") # 🚨 Falha no teste se o valor estiver incorreto
                else: # ✅ Se apenas a presença da chave for verificada (sem valor específico)
                    if expected_result_key in response_json: # ✅ Verifica se a chave esperada está presente no JSON da resposta
                        colored_print_success(f"✅ {test_name} OK: Chave '{expected_result_key}' presente na resposta.") # 🟢 Imprime mensagem de sucesso no console
                    else: # ❌ Se a chave esperada estiver ausente na resposta JSON
                        colored_print_failure(f"❌ {test_name} FALHOU: Chave '{expected_result_key}' ausente na resposta JSON. Response: {response_json}") # 🔴 Imprime mensagem de falha no console
                        self.fail(f"Chave '{expected_result_key}' ausente na resposta JSON.") # 🚨 Falha no teste se a chave estiver ausente
            except json.JSONDecodeError: # ❗ Captura exceção se houver erro ao decodificar o JSON da resposta
                self.fail(f"❌ {test_name} FALHOU: Erro ao decodificar JSON. Response text: {resposta.text}") # 🚨 Falha no teste se a resposta não for um JSON válido
        return resposta # ➡️ Retorna o objeto de resposta para inspeção adicional

    def test_rota_saude(self):
        """Testa o endpoint público '/saude' para verificar se a API está saudável."""
        resposta = requests.get(f"{API_BASE_URL}/saude", verify=VERIFY_SSL_CERT) # 📧 Faz requisição GET para o endpoint /saude
        self.assertEqual(resposta.status_code, 200, colored_print_failure(f"Rota /saude falhou, status code: {resposta.status_code}")) # 🚨 Falha se o status code não for 200
        if resposta.status_code == 200: # ✅ Se o status code for 200 (OK)
            try:
                response_json = resposta.json() # 🗄️ Tenta decodificar a resposta como JSON
                if response_json.get("status") == "OK": # ✅ Verifica se o status no JSON é 'OK'
                    colored_print_success(f"✅ Teste /saude OK: Status 'OK' encontrado na resposta JSON.") # 🟢 Imprime mensagem de sucesso
                else: # ❌ Se o status não for 'OK'
                    colored_print_failure(f"❌ /saude - status incorreto na resposta JSON. Esperado 'OK', obtido: '{response_json.get('status')}'") # 🔴 Imprime mensagem de falha com o status incorreto
                    self.assertEqual(response_json.get("status"), "OK") # 🚨 Falha se o status JSON não for 'OK'

                if "mensagem" in response_json: # ✅ Verifica se a chave 'mensagem' está presente no JSON
                    colored_print_success(f"✅ Teste /saude OK: Chave 'mensagem' encontrada na resposta JSON.") # 🟢 Imprime mensagem de sucesso
                else: # ❌ Se a chave 'mensagem' estiver ausente
                    colored_print_failure(f"❌ /saude - chave 'mensagem' ausente na resposta JSON.") # 🔴 Imprime mensagem de falha informando que a chave está ausente
                    self.assertIn("mensagem", response_json) # 🚨 Falha se a chave 'mensagem' estiver ausente

                if "version" in response_json: # ✅ Verifica se a chave 'version' está presente no JSON
                    colored_print_success(f"✅ Teste /saude OK: Chave 'version' encontrada na resposta JSON.") # 🟢 Imprime mensagem de sucesso
                else: # ⚠️ Se a chave 'version' estiver ausente (pode ser opcional)
                    colored_print_warning(f"⚠️ /saude - chave 'version' ausente na resposta JSON (pode ser opcional).") # 🟡 Imprime mensagem de aviso indicando que a chave está ausente (aviso, não falha)

            except json.JSONDecodeError: # ❗ Captura exceção se a resposta não for um JSON válido
                colored_print_failure(f"❌ /saude - Resposta não é um JSON válido: {resposta.text}") # 🔴 Imprime mensagem de falha se a resposta não for JSON
                self.fail("Resposta /saude não é um JSON válido") # 🚨 Falha no teste se a resposta não for JSON válida
        else: # ❌ Se o status code da resposta não for 200
            colored_print_failure(f"❌ Rota /saude falhou, status code: {resposta.status_code}") # 🔴 Imprime mensagem de falha com o status code incorreto

    def test_rota_somar_numeros_positivos(self):
        """Testa o endpoint '/somar' com uma lista de números inteiros positivos válidos."""
        numeros = [1, 2, 3, 4, 5] # 🔢 Lista de números positivos para o teste
        soma_esperada = sum(numeros) # ➕ Calcula a soma esperada dos números
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="resultado", expected_result_value=soma_esperada, test_name="/somar números positivos") # 🧪 Executa o teste genérico da rota POST para '/somar'

    def test_rota_calcular_media_numeros_positivos(self):
        """Testa o endpoint '/calcular_media' com uma lista de números inteiros positivos válidos."""
        numeros = [1, 2, 3, 4, 5] # 🔢 Lista de números positivos para o teste
        media_esperada = sum(numeros) / len(numeros) # ➗ Calcula a média esperada dos números
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="media", expected_result_value=media_esperada, test_name="/calcular_media números positivos") # 🧪 Executa o teste genérico da rota POST para '/calcular_media'

    def test_rota_somar_lista_vazia_erro_422(self):
        """Testa o endpoint '/somar' com uma lista vazia, esperando um erro de status 422."""
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": []}, expected_status=422, test_name="/somar lista vazia (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/somar' com lista vazia e status 422 esperado

    def test_rota_calcular_media_lista_vazia_retorna_none(self):
        """Testa o endpoint '/calcular_media' com uma lista vazia, esperando que retorne média como None."""
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": []}, expected_status=200, expected_result_key="media", expected_result_value=None, test_name="/calcular_media lista vazia (media None)") # 🧪 Executa o teste genérico da rota POST para '/calcular_media' com lista vazia e média None esperada

    def test_rota_somar_input_nao_lista_erro_422(self):
        """Testa o endpoint '/somar' com um input que não é uma lista, esperando um erro 422."""
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": "string"}, expected_status=422, test_name="/somar input não lista (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/somar' com input string e status 422 esperado

    def test_rota_calcular_media_input_nao_lista_erro_422(self):
        """Testa o endpoint '/calcular_media' com um input que não é uma lista, esperando um erro 422."""
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": "string"}, expected_status=422, test_name="/calcular_media input não lista (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/calcular_media' com input string e status 422 esperado

    def test_rota_somar_lista_com_nao_inteiros_erro_422(self):
        """Testa o endpoint '/somar' com uma lista contendo elementos não inteiros, esperando erro 422."""
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": [1, 2, "a", 4]}, expected_status=422, test_name="/somar lista com não inteiros (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/somar' com lista de não inteiros e status 422 esperado

    def test_rota_calcular_media_lista_com_nao_inteiros_erro_422(self):
        """Testa o endpoint '/calcular_media' com uma lista contendo elementos não inteiros, esperando erro 422."""
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": [1, 2, "a", 4]}, expected_status=422, test_name="/calcular_media lista com não inteiros (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/calcular_media' com lista de não inteiros e status 422 esperado

    def test_rota_somar_lista_com_none_erro_422(self):
        """Testa o endpoint '/somar' com uma lista contendo o valor None, esperando erro 422."""
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": [1, 2, None, 4]}, expected_status=422, test_name="/somar lista com None (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/somar' com lista contendo None e status 422 esperado

    def test_rota_calcular_media_lista_com_none_erro_422(self):
        """Testa o endpoint '/calcular_media' com uma lista contendo o valor None, esperando erro 422."""
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": [1, 2, None, 4]}, expected_status=422, test_name="/calcular_media lista com None (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/calcular_media' com lista contendo None e status 422 esperado

    def test_rota_somar_lista_com_float_como_string_erro_422(self):
        """Testa o endpoint '/somar' com uma lista contendo um float como string (e.g., "2.5"), esperando erro 422."""
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": [1, 2, "2.5", 4]}, expected_status=422, test_name="/somar lista float string (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/somar' com lista contendo float string e status 422 esperado

    def test_rota_calcular_media_lista_com_float_como_string_erro_422(self):
        """Testa o endpoint '/calcular_media' com uma lista contendo um float como string (e.g., "2.5"), esperando erro 422."""
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": [1, 2, "2.5", 4]}, expected_status=422, test_name="/calcular_media lista float string (erro 422)") # 🧪 Executa o teste genérico da rota POST para '/calcular_media' com lista contendo float string e status 422 esperado

    def test_rota_somar_lista_com_string_int_ok(self):
        """Testa o endpoint '/somar' com uma lista contendo strings que representam inteiros, esperando sucesso."""
        numeros = [1, 2, "3", 4] # 🔢 Lista contendo strings que são inteiros
        soma_esperada = sum([1, 2, 3, 4]) # ➕ Calcula a soma esperada (convertendo strings para int)
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="resultado", expected_result_value=soma_esperada, test_name="/somar lista com string int (OK)") # 🧪 Executa o teste genérico da rota POST para '/somar' com lista de string int e sucesso esperado

    def test_rota_calcular_media_lista_com_string_int_ok(self):
        """Testa o endpoint '/calcular_media' com uma lista contendo strings que representam inteiros, esperando sucesso."""
        numeros = [1, 2, "3", 4] # 🔢 Lista contendo strings que são inteiros
        media_esperada = sum([1, 2, 3, 4]) / len([1, 2, 3, 4]) # ➗ Calcula a média esperada (convertendo strings para int)
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="media", expected_result_value=media_esperada, test_name="/calcular_media lista string int (OK)") # 🧪 Executa o teste genérico da rota POST para '/calcular_media' com lista de string int e sucesso esperado

    def test_rota_somar_lista_com_float_int_string_ok(self):
        """Testa o endpoint '/somar' com uma lista mista de floats (como int), ints e strings de inteiros, esperando sucesso."""
        numeros = [1, 2.0, "3", 4] # 🔢 Lista mista de floats (como int), ints e strings de inteiros
        soma_esperada = sum([1, 2, 3, 4]) # ➕ Calcula a soma esperada (convertendo floats e strings para int)
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="resultado", expected_result_value=soma_esperada, test_name="/somar lista float int string (OK)") # 🧪 Executa o teste genérico da rota POST para '/somar' com lista mista e sucesso esperado

    def test_rota_calcular_media_lista_com_float_int_string_ok(self):
        """Testa o endpoint '/calcular_media' com uma lista mista de floats (como int), ints e strings de inteiros, esperando sucesso."""
        numeros = [1, 2.0, "3", 4] # 🔢 Lista mista de floats (como int), ints e strings de inteiros
        media_esperada = sum([1, 2, 3, 4]) / len([1, 2, 3, 4]) # ➗ Calcula a média esperada (convertendo floats e strings para int)
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="media", expected_result_value=media_esperada, test_name="/calcular_media lista float int string (OK)") # 🧪 Executa o teste genérico da rota POST para '/calcular_media' com lista mista e sucesso esperado

if __name__ == "__main__":
    """Executa a suíte de testes quando o script é rodado diretamente."""
    suite = unittest.TestSuite() # 🧪 Cria uma suíte de testes
    suite.addTest(unittest.makeSuite(ApiTests)) # 🧪 Adiciona todos os testes da classe ApiTests à suíte

    runner = unittest.TextTestRunner(verbosity=2) # 🏃‍♂️ Cria um runner de testes de texto com verbosidade 2 (mais detalhes na saída)
    test_results = runner.run(suite) # 🏃‍♂️ Executa a suíte de testes e obtém os resultados