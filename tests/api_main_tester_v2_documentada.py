import requests
import json
import os
import unittest
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

API_BASE_URL = os.environ.get("API_TEST_URL", "https://localhost:8882")
VERIFY_SSL_CERT = os.environ.get("API_VERIFY_SSL", False) == 'True'

ADMIN_TOKEN = None

def obter_token_admin():
    """
    Obtém um token JWT de administrador para autenticação em testes.
    """
    global ADMIN_TOKEN
    token_url = f"{API_BASE_URL}/token_admin"
    credenciais = {"username": "admin", "password": "admin"}
    try:
        resposta = requests.post(token_url, json=credenciais, verify=VERIFY_SSL_CERT)
        resposta.raise_for_status()
        ADMIN_TOKEN = resposta.json().get("access_token")
        colored_print_success("🔑 Token ADMIN obtido.")
        return ADMIN_TOKEN
    except requests.exceptions.RequestException as e:
        print(Fore.RED + Style.BRIGHT + f"🔥 Erro ao obter token ADMIN: {e}" + Style.RESET_ALL)
        return None

def colored_print_success(msg):
    """Imprime mensagem de sucesso em verde."""
    print(Fore.GREEN + Style.BRIGHT + "✅ " + msg + Style.RESET_ALL)

def colored_print_failure(msg):
    """Imprime mensagem de falha em vermelho."""
    print(Fore.RED + Style.BRIGHT + "❌ " + msg + Style.RESET_ALL)

def colored_print_info(msg):
    """Imprime mensagem de informação em ciano."""
    print(Fore.CYAN + Style.BRIGHT + "ℹ️  " + msg + Style.RESET_ALL)

def colored_print_warning(msg):
    """Imprime mensagem de aviso em amarelo."""
    print(Fore.YELLOW + Style.BRIGHT + "⚠️  " + msg + Style.RESET_ALL)

def colored_print_header(msg):
    """Imprime cabeçalho em azul."""
    print(Back.BLUE + Fore.WHITE + Style.BRIGHT + " " + msg + " " + Style.RESET_ALL)


class TestApiProd(unittest.TestCase):
    """
    Suíte de testes simplificada para API de produção.
    """

    def setUp(self):
        """
        Configuração inicial: Obtém token ADMIN e define headers.
        """
        global ADMIN_TOKEN
        if not ADMIN_TOKEN:
            ADMIN_TOKEN = obter_token_admin()
            if not ADMIN_TOKEN:
                self.skipTest("Token ADMIN não obtido, pulando testes.")
        self.admin_token = ADMIN_TOKEN
        self.headers_admin = {"Authorization": f"Bearer {self.admin_token}"}

    def _testar_rota_post(self, url_path, data, expected_status=200, expected_result_key=None, expected_result_value=None, test_name="Rota POST"):
        """
        Função auxiliar para testar rotas POST e validar a resposta.
        """
        url = f"{API_BASE_URL}{url_path}"
        colored_print_info(f"➡️  Testando rota: {url_path} - Dados: {data}")

        resposta = requests.post(url, headers=self.headers_admin, json=data, verify=VERIFY_SSL_CERT)

        if resposta.status_code != expected_status:
            colored_print_failure(f"❌ {test_name} FALHOU: Status code incorreto. Esperado: {expected_status}, Obtido: {resposta.status_code}. Response Body: {resposta.text}")
            self.assertEqual(resposta.status_code, expected_status)
            return

        if expected_status < 400 and expected_result_key:
            try:
                response_json = resposta.json()
                actual_value = response_json.get(expected_result_key)
                self.assertEqual(actual_value, expected_result_value, f"Valor incorreto para chave '{expected_result_key}'. Esperado: {expected_result_value}, Obtido: {actual_value}")
                colored_print_success(f"✅ {test_name} OK: Valor de '{expected_result_key}' validado. ({expected_result_value})")
            except json.JSONDecodeError:
                self.fail(f"❌ {test_name} FALHOU: Erro ao decodificar JSON. Response text: {resposta.text}")


    def test_soma_inteiros_validos(self):
        """Testa a rota /somar com inteiros válidos."""
        self._testar_rota_post("/somar", {"numeros": [1, 2, 3, 4]}, expected_status=200, expected_result_key="resultado", expected_result_value=10, test_name="soma_inteiros_validos")

    def test_soma_strings_numericas_validas(self):
        """Testa a rota /somar com strings numéricas válidas."""
        self._testar_rota_post("/somar", {"numeros": ["5", "10", "15"]}, expected_status=200, expected_result_key="resultado", expected_result_value=30, test_name="soma_strings_numericas_validas")

    def test_soma_lista_vazia_erro(self):
        """Testa a rota /somar com lista vazia, esperando erro."""
        self._testar_rota_post("/somar", {"numeros": []}, expected_status=422, test_name="soma_lista_vazia_erro")

    def test_soma_tipo_invalido_string_erro(self):
        """Testa a rota /somar com tipo de input inválido (string), esperando erro."""
        self._testar_rota_post("/somar", {"numeros": "nao_eh_lista"}, expected_status=422, test_name="soma_tipo_invalido_string_erro")

    def test_soma_lista_com_string_erro(self):
        """Testa a rota /somar com lista contendo string, esperando erro."""
        self._testar_rota_post("/somar", {"numeros": [1, 2, "a", 4]}, expected_status=422, test_name="soma_lista_com_string_erro")

    def test_soma_lista_com_float_sem_perda(self):
        """Testa a rota /somar com lista contendo float sem perda de precisão."""
        self._testar_rota_post("/somar", {"numeros": [1, 2, 3.0, 4]}, expected_status=200, expected_result_key="resultado", expected_result_value=10, test_name="soma_lista_com_float_sem_perda")

    def test_soma_lista_com_float_com_perda_erro(self):
        """Testa a rota /somar com lista contendo float com perda de precisão, esperando erro."""
        self._testar_rota_post("/somar", {"numeros": [1, 2, 3.5, 4]}, expected_status=422, test_name="soma_lista_com_float_com_perda_erro")

    def test_soma_lista_com_none_erro(self):
        """Testa a rota /somar com lista contendo None, esperando erro."""
        self._testar_rota_post("/somar", {"numeros": [1, 2, None, 4]}, expected_status=422, test_name="soma_lista_com_none_erro")


    def test_media_inteiros_validos(self):
        """Testa a rota /calcular_media com inteiros válidos."""
        self._testar_rota_post("/calcular_media", {"numeros": [1, 2, 3, 4]}, expected_status=200, expected_result_key="media", expected_result_value=2.5, test_name="media_inteiros_validos")

    def test_media_strings_numericas_validas(self):
        """Testa a rota /calcular_media com strings numéricas válidas."""
        self._testar_rota_post("/calcular_media", {"numeros": ["5", "10", "15"]}, expected_status=200, expected_result_key="media", expected_result_value=10.0, test_name="media_strings_numericas_validas")

    def test_media_lista_vazia_ok(self):
        """Testa a rota /calcular_media com lista vazia, esperando OK e media None."""
        self._testar_rota_post("/calcular_media", {"numeros": []}, expected_status=200, expected_result_key="media", expected_result_value=None, test_name="media_lista_vazia_ok")

    def test_media_tipo_invalido_string_erro(self):
        """Testa a rota /calcular_media com tipo de input inválido (string), esperando erro."""
        self._testar_rota_post("/calcular_media", {"numeros": "nao_eh_lista"}, expected_status=422, test_name="media_tipo_invalido_string_erro")

    def test_media_lista_com_string_erro(self):
        """Testa a rota /calcular_media com lista contendo string, esperando erro."""
        self._testar_rota_post("/calcular_media", {"numeros": [1, 2, "a", 4]}, expected_status=422, test_name="media_lista_com_string_erro")

    def test_media_lista_com_float_sem_perda(self):
        """Testa a rota /calcular_media com lista contendo float sem perda de precisão."""
        self._testar_rota_post("/calcular_media", {"numeros": [1, 2, 3.0, 4]}, expected_status=200, expected_result_key="media", expected_result_value=2.5, test_name="media_lista_com_float_sem_perda")

    def test_media_lista_com_float_com_perda_erro(self):
        """Testa a rota /calcular_media com lista contendo float com perda de precisão, esperando erro."""
        self._testar_rota_post("/calcular_media", {"numeros": [1, 2, 3.5, 4]}, expected_status=422, test_name="media_lista_com_float_com_perda_erro")

    def test_media_lista_com_none_erro(self):
        """Testa a rota /calcular_media com lista contendo None, esperando erro."""
        self._testar_rota_post("/calcular_media", {"numeros": [1, 2, None, 4]}, expected_status=422, test_name="media_lista_com_none_erro")

    def test_media_divisao_por_zero(self):
        """Testa a rota /calcular_media com divisão por zero (todos os números são zero)."""
        self._testar_rota_post("/calcular_media", {"numeros": [0, 0, 0]}, expected_status=200, expected_result_key="media", expected_result_value=0.0, test_name="media_divisao_por_zero")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestApiProd))

    runner = unittest.TextTestRunner(verbosity=2)
    test_results = runner.run(suite)

    total_tests = suite.countTestCases()
    passed_tests = total_tests - (len(test_results.errors) + len(test_results.failures))
    failed_tests = total_tests - passed_tests

    if total_tests > 0:
        percentage_passed = (passed_tests / total_tests) * 100
        percentage_failed = (failed_tests / total_tests) * 100
    else:
        percentage_passed = 0
        percentage_failed = 0

    print(Fore.BLUE + Style.BRIGHT + "\n📊 Resumo dos Testes:" + Style.RESET_ALL)
    if percentage_passed == 100:
        print(Fore.GREEN + Style.BRIGHT + "🏆 Todos os testes PASSARAM! 🎉" + Style.RESET_ALL)
    elif percentage_failed == 100:
        print(Fore.RED + Style.BRIGHT + "🚨 Todos os testes FALHARAM! 💔" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + Style.BRIGHT + f"✅ Passou: {percentage_passed:.2f}% ({passed_tests}/{total_tests})" + Style.RESET_ALL)
        print(Fore.RED + Style.BRIGHT + f"❌ Reprovou: {percentage_failed:.2f}% ({failed_tests}/{total_tests})" + Style.RESET_ALL)

    if percentage_passed >= 70:
        status_emoji = "😎👍"
        status_color = Fore.GREEN
    elif percentage_passed >= 50:
        status_emoji = "🙂"
        status_color = Fore.YELLOW
    else:
        status_emoji = "😞💔"
        status_color = Fore.RED

    print(status_color + Style.BRIGHT + f"\n✨ Status Geral: {status_emoji} {percentage_passed:.2f}% de Aprovação! {status_emoji}" + Style.RESET_ALL)
    print(Fore.BLUE + Style.BRIGHT + "\n🏁 Testes Simplificados e Diretos da API de Produção Concluídos." + Style.RESET_ALL)