import requests
import json
import os
import unittest
import time
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

API_BASE_URL = os.environ.get("API_TEST_URL", "https://localhost:8882")
VERIFY_SSL_CERT = os.environ.get("API_VERIFY_SSL", False) == 'True'
LOG_DIR = "test_logs"
LOG_FILE = os.path.join(LOG_DIR, "api-test-log.json")

ADMIN_TOKEN = None

def obter_token_admin():
    global ADMIN_TOKEN
    token_url = f"{API_BASE_URL}/token_admin"
    credenciais = {"username": "admin", "password": "admin"}
    try:
        resposta = requests.post(token_url, json=credenciais, verify=VERIFY_SSL_CERT)
        resposta.raise_for_status()
        ADMIN_TOKEN = resposta.json().get("access_token")
        return ADMIN_TOKEN
    except requests.exceptions.RequestException as e:
        print(Fore.RED + Style.BRIGHT + f"🔥 Erro ao obter token ADMIN: {e}" + Style.RESET_ALL)
        return None

def colored_print_success(msg):
    print(Fore.GREEN + Style.BRIGHT + "✅ " + msg + Style.RESET_ALL)

def colored_print_failure(msg):
    print(Fore.RED + Style.BRIGHT + "❌ " + msg + Style.RESET_ALL)

def colored_print_info(msg):
    print(Fore.CYAN + Style.BRIGHT + "ℹ️  " + msg + Style.RESET_ALL)

def colored_print_warning(msg):
    print(Fore.YELLOW + Style.BRIGHT + "⚠️  " + msg + Style.RESET_ALL)

def colored_print_header(msg):
    print(Back.BLUE + Fore.WHITE + Style.BRIGHT + " " + msg + " " + Style.RESET_ALL)

class ApiTests(unittest.TestCase):

    def setUp(self):
        global ADMIN_TOKEN
        if not ADMIN_TOKEN:
            ADMIN_TOKEN = obter_token_admin()
            if not ADMIN_TOKEN:
                self.skipTest("Token ADMIN não obtido, pulando testes protegidos.")
        self.admin_token = ADMIN_TOKEN
        self.headers_admin = {"Authorization": f"Bearer {self.admin_token}"}
        self.log_entries = []

    def tearDown(self):
        end_time = time.time()
        test_duration = end_time - self.start_test_time
        status = "PASSOU" if not self._outcome.errors and not self._outcome.failures else "FALHOU"

        log_entry = {
            "test_name": self._testMethodName,
            "status": status,
            "duration_seconds": f"{test_duration:.4f}",
            "timestamp": datetime.now().isoformat(),
            "details": self.current_test_log
        }
        self.log_entries.append(log_entry)
        self._save_log_to_file()


    def _start_test_logging(self, test_name):
        self.current_test_log = []
        self.start_test_time = time.time()

    def _log_request_response(self, method, url, headers, data, response):
        log_data = {
            "request": {
                "method": method,
                "url": url,
                "headers": headers,
                "data": data if method == 'POST' else None,
                "json": data if method == 'POST' else None
            },
            "response": {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text
            }
        }
        self.current_test_log.append(log_data)

    def _save_log_to_file(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        log_header = {"test_run_timestamp": datetime.now().isoformat(), "test_suite": "ApiTests"}

        try:
            file_exists = os.path.exists(LOG_FILE)
            with open(LOG_FILE, 'a') as f:
                if not file_exists:
                    f.write('{"test_runs": [\n')
                else:
                    f.write(',\n')

                json.dump(log_header, f, indent=4, ensure_ascii=False)
                f.write(',\n"tests": [\n')

                for i, entry in enumerate(self.log_entries):
                    json.dump(entry, f, indent=4, ensure_ascii=False)
                    if i < len(self.log_entries) - 1:
                        f.write(',')
                    f.write('\n')

                f.write(']\n}')
                self.log_entries = []

        except Exception as e:
            colored_print_failure(f"❌ Erro ao salvar log em '{LOG_FILE}': {e}")


    def _testar_rota_post(self, url_path, token_headers, data, expected_status=200, expected_result_key=None, expected_result_value=None, test_name="Rota POST"):
        url = f"{API_BASE_URL}{url_path}"
        self._start_test_logging(test_name)

        resposta = requests.post(url, headers=token_headers, json=data, verify=VERIFY_SSL_CERT)
        self._log_request_response('POST', url, token_headers, data, resposta)

        if resposta.status_code != expected_status:
            colored_print_failure(f"❌ {test_name} FALHOU: Status code incorreto. Esperado: {expected_status}, Obtido: {resposta.status_code}. Response Body: {resposta.text}")
            self.assertEqual(resposta.status_code, expected_status)
            return

        if expected_status < 400 and expected_result_key:
            try:
                response_json = resposta.json()
                actual_value = response_json.get(expected_result_key)
                if expected_result_value is not None:
                    if actual_value == expected_result_value:
                        colored_print_success(f"✅ {test_name} OK: Valor de '{expected_result_key}' validado. ({expected_result_value})")
                    else:
                        colored_print_failure(f"❌ {test_name} FALHOU: Valor incorreto para chave '{expected_result_key}'. Esperado: {expected_result_value}, Obtido: {actual_value}. Response: {response_json}")
                        self.fail(f"Valor incorreto para chave '{expected_result_key}'. Esperado: {expected_result_value}, Obtido: {actual_value}")
                else:
                    if expected_result_key in response_json:
                        colored_print_success(f"✅ {test_name} OK: Chave '{expected_result_key}' presente na resposta.")
                    else:
                        colored_print_failure(f"❌ {test_name} FALHOU: Chave '{expected_result_key}' ausente na resposta JSON. Response: {response_json}")
                        self.fail(f"Chave '{expected_result_key}' ausente na resposta JSON.")
            except json.JSONDecodeError:
                self.fail(f"❌ {test_name} FALHOU: Erro ao decodificar JSON. Response text: {resposta.text}")
        return resposta


    def test_rota_saude(self):
        resposta = requests.get(f"{API_BASE_URL}/saude", verify=VERIFY_SSL_CERT)
        self.assertEqual(resposta.status_code, 200, colored_print_failure(f"Rota /saude falhou, status code: {resposta.status_code}"))
        if resposta.status_code == 200:
            try:
                response_json = resposta.json()
                if response_json.get("status") == "OK":
                    colored_print_success(f"✅ Teste /saude OK: Status 'OK' encontrado na resposta JSON.")
                else:
                    colored_print_failure(f"❌ /saude - status incorreto na resposta JSON. Esperado 'OK', obtido: '{response_json.get('status')}'")
                    self.assertEqual(response_json.get("status"), "OK")

                if "mensagem" in response_json:
                    colored_print_success(f"✅ Teste /saude OK: Chave 'mensagem' encontrada na resposta JSON.")
                else:
                    colored_print_failure(f"❌ /saude - chave 'mensagem' ausente na resposta JSON.")
                    self.assertIn("mensagem", response_json)

                if "version" in response_json:
                    colored_print_success(f"✅ Teste /saude OK: Chave 'version' encontrada na resposta JSON.")
                else:
                    colored_print_warning(f"⚠️ /saude - chave 'version' ausente na resposta JSON (pode ser opcional).")

            except json.JSONDecodeError:
                colored_print_failure(f"❌ /saude - Resposta não é um JSON válido: {resposta.text}")
                self.fail("Resposta /saude não é um JSON válido")
        else:
            colored_print_failure(f"❌ Rota /saude falhou, status code: {resposta.status_code}")


    def test_rota_somar_numeros_positivos(self):
        numeros = [1, 2, 3, 4, 5]
        soma_esperada = sum(numeros)
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="resultado", expected_result_value=soma_esperada, test_name="/somar números positivos")

    def test_rota_calcular_media_numeros_positivos(self):
        numeros = [1, 2, 3, 4, 5]
        media_esperada = sum(numeros) / len(numeros)
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="media", expected_result_value=media_esperada, test_name="/calcular_media números positivos")

    def test_rota_somar_lista_vazia_erro_422(self):
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": []}, expected_status=422, test_name="/somar lista vazia (erro 422)")

    def test_rota_calcular_media_lista_vazia_retorna_none(self):
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": []}, expected_status=200, expected_result_key="media", expected_result_value=None, test_name="/calcular_media lista vazia (media None)")

    def test_rota_somar_input_nao_lista_erro_422(self):
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": "string"}, expected_status=422, test_name="/somar input não lista (erro 422)")

    def test_rota_calcular_media_input_nao_lista_erro_422(self):
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": "string"}, expected_status=422, test_name="/calcular_media input não lista (erro 422)")

    def test_rota_somar_lista_com_nao_inteiros_erro_422(self):
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": [1, 2, "a", 4]}, expected_status=422, test_name="/somar lista com não inteiros (erro 422)")

    def test_rota_calcular_media_lista_com_nao_inteiros_erro_422(self):
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": [1, 2, "a", 4]}, expected_status=422, test_name="/calcular_media lista com não inteiros (erro 422)")

    def test_rota_somar_lista_com_none_erro_422(self):
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": [1, 2, None, 4]}, expected_status=422, test_name="/somar lista com None (erro 422)")

    def test_rota_calcular_media_lista_com_none_erro_422(self):
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": [1, 2, None, 4]}, expected_status=422, test_name="/calcular_media lista com None (erro 422)")

    def test_rota_somar_lista_com_float_como_string_erro_422(self):
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": [1, 2, "2.5", 4]}, expected_status=422, test_name="/somar lista float string (erro 422)")

    def test_rota_calcular_media_lista_com_float_como_string_erro_422(self):
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": [1, 2, "2.5", 4]}, expected_status=422, test_name="/calcular_media lista float string (erro 422)")

    def test_rota_somar_lista_com_string_int_ok(self):
        numeros = [1, 2, "3", 4]
        soma_esperada = sum([1, 2, 3, 4])
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="resultado", expected_result_value=soma_esperada, test_name="/somar lista com string int (OK)")

    def test_rota_calcular_media_lista_com_string_int_ok(self):
        numeros = [1, 2, "3", 4]
        media_esperada = sum([1, 2, 3, 4]) / len([1, 2, 3, 4])
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="media", expected_result_value=media_esperada, test_name="/calcular_media lista string int (OK)")

    def test_rota_somar_lista_com_float_int_string_ok(self):
        numeros = [1, 2.0, "3", 4]
        soma_esperada = sum([1, 2, 3, 4])
        self._testar_rota_post("/somar", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="resultado", expected_result_value=soma_esperada, test_name="/somar lista float int string (OK)")

    def test_rota_calcular_media_lista_com_float_int_string_ok(self):
        numeros = [1, 2.0, "3", 4]
        media_esperada = sum([1, 2, 3, 4]) / len([1, 2, 3, 4])
        self._testar_rota_post("/calcular_media", self.headers_admin, {"numeros": numeros}, expected_status=200, expected_result_key="media", expected_result_value=media_esperada, test_name="/calcular_media lista float int string (OK)")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ApiTests))

    runner = unittest.TextTestRunner(verbosity=2)
    test_results = runner.run(suite)