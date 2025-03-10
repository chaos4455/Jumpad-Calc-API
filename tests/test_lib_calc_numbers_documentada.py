# -*- coding: utf-8 -*-
"""
Script de Testes Unitários para a Biblioteca calc_numbers (Classe Numbers)

Este script Python implementa testes unitários abrangentes para a biblioteca
`calc_numbers`, especificamente para a classe `Numbers`. Utiliza o framework `pytest`
para definir e executar os testes, e registra os resultados detalhados em arquivos
de log JSON para análise e rastreamento.

Os testes unitários cobrem as seguintes funcionalidades da classe `Numbers`:

    - Método `sum_numbers`: Testes para diferentes cenários de entrada, incluindo listas
      de inteiros válidos, strings numéricas, listas vazias, tipos inválidos, listas com
      strings não numéricas, listas com floats (com e sem perda de precisão), e listas com None.

    - Método `calculate_average`: Testes similares ao `sum_numbers`, mas focados no cálculo
      da média, incluindo casos de lista vazia (que deve retornar None), divisão por zero
      (comportamento esperado para listas de zeros), e os mesmos cenários de validação de entrada
      aplicados ao `sum_numbers`.

O script inclui funcionalidades para:

    - Geração de logs de teste em formato JSON, com timestamps e detalhes de cada caso de teste.
    - Organização dos logs em diretórios, com nomes de arquivos sequenciais para evitar sobrescrita.
    - Uso de `pytest.raises` para testar o lançamento correto de exceções esperadas.
    - Uso de `pytest.approx` para comparação aproximada de números de ponto flutuante em testes de média.
    - Mensagens informativas no console sobre o início e a conclusão dos testes, e o local dos logs.

Para executar os testes, basta rodar este script Python diretamente. Os resultados
detalhados serão salvos em arquivos JSON no diretório `test_logs/`.

Bibliotecas Utilizadas:
    - pytest: Framework de testes Python para executar e organizar os testes unitários.
    - os: Para manipulação de arquivos e diretórios (e.g., criação de diretório de logs).
    - json: Para serialização e escrita dos resultados dos testes em formato JSON.
    - datetime: Para geração de timestamps para os logs de teste.
    - bibliotecas.calc_numbers.Numbers: A biblioteca e classe `Numbers` sendo testadas.

Diretórios e Arquivos Gerados:
    - test_logs/: Diretório onde os arquivos de log JSON são salvos.
        - log_teste_*.json: Arquivos de log individuais para cada execução de teste, contendo
          os resultados detalhados de cada caso de teste, status (PASSOU, FALHOU, ERRO),
          entradas, saídas esperadas e reais, e informações de exceções (se aplicável).

Execução:
    Execute este script diretamente para iniciar os testes unitários da biblioteca `calc_numbers`.
    Os logs serão gerados no diretório `test_logs/`.

Criado por: Elias Andrade
Data de Criação: 10 de Março de 2025
"""
import sys
import os
import json
import datetime
import pytest # 🧪 Framework de testes pytest
from bibliotecas.calc_numbers import Numbers # 📚 Importa a classe Numbers a ser testada

DIRETORIO_LOGS_TESTE = "test_logs" # 🗂️ Diretório para salvar os logs de teste
if not os.path.exists(DIRETORIO_LOGS_TESTE): # 📁 Cria o diretório de logs se não existir
    os.makedirs(DIRETORIO_LOGS_TESTE)

def obter_proximo_nome_arquivo_log():
    """
    Gera um nome de arquivo de log único e sequencial no diretório de logs.

    Verifica sequencialmente a existência de arquivos de log com nomes como 'log_teste_1.json',
    'log_teste_2.json', etc., e retorna o primeiro nome de arquivo que não existir, garantindo
    que cada execução de teste tenha seu próprio arquivo de log, sem sobrescrever logs anteriores.

    Returns:
        str: O caminho completo para o próximo arquivo de log disponível.
    """
    contador_logs = 1 # 🔢 Inicia o contador para nomes de arquivos de log
    while True: # 🔄 Loop infinito até encontrar um nome de arquivo disponível
        nome_arquivo_log = os.path.join(DIRETORIO_LOGS_TESTE, f"log_teste_{contador_logs}.json") # 📝 Monta o nome do arquivo de log com contador sequencial
        if not os.path.exists(nome_arquivo_log): # ✅ Verifica se o arquivo de log já existe
            return nome_arquivo_log # 🚀 Retorna o nome de arquivo disponível encontrado
        contador_logs += 1 # ➕ Incrementa o contador para tentar o próximo nome de arquivo

def salvar_log_teste(dados_log):
    """
    Salva os dados de log de teste em um arquivo JSON.

    Recebe um dicionário contendo os dados de log e escreve-os em um arquivo JSON formatado.
    O nome do arquivo é gerado automaticamente por `obter_proximo_nome_arquivo_log()` para
    garantir que seja único e sequencial. Imprime uma mensagem no console informando o local
    onde os resultados dos testes foram salvos.

    Args:
        dados_log (dict): Um dicionário contendo os resultados e detalhes dos testes a serem salvos.
    """
    nome_arquivo_log = obter_proximo_nome_arquivo_log() # 📝 Obtém um nome de arquivo de log único
    with open(nome_arquivo_log, 'w', encoding='utf-8') as arquivo: # 📝 Abre o arquivo de log em modo de escrita ('w') com encoding UTF-8
        json.dump(dados_log, arquivo, indent=4, ensure_ascii=False) # 💾 Escreve os dados de log em formato JSON formatado no arquivo
    print(f"Resultados dos testes salvos em: {nome_arquivo_log}") # 💬 Imprime mensagem informando onde os logs foram salvos

def executar_testes():
    """
    Executa a suíte de testes para a biblioteca calc_numbers, abrangendo soma e média.

    Inicializa a classe `Numbers`, define casos de teste para os métodos `sum_numbers` e
    `calculate_average`, executa cada caso de teste chamando `executar_caso_teste`, e
    agrega os resultados. Ao final, prepara os dados de log, incluindo um timestamp de
    execução, e chama `salvar_log_teste` para persistir os resultados em um arquivo JSON.
    """
    calculadora = Numbers() # ➕ Instancia a classe Numbers para executar os testes
    resultados_teste = [] # 📝 Lista para armazenar os resultados de cada caso de teste

    casos_teste_soma = [ # 🧪 Casos de teste para o método sum_numbers
        {"nome": "soma_inteiros_validos", "entrada": [1, 2, 3, 4], "saida_esperada": 10, "espera_excecao": None}, # ✅ Teste de soma com inteiros válidos
        {"nome": "soma_strings_numericas_validas", "entrada": ["5", "10", "15"], "saida_esperada": 30, "espera_excecao": None}, # ✅ Teste de soma com strings numéricas válidas
        {"nome": "soma_lista_vazia", "entrada": [], "saida_esperada": None, "espera_excecao": ValueError}, # ❌ Teste de soma com lista vazia (espera ValueError)
        {"nome": "soma_tipo_invalido_string", "entrada": "nao_eh_lista", "saida_esperada": None, "espera_excecao": TypeError}, # ❌ Teste de soma com tipo de entrada inválido (string, espera TypeError)
        {"nome": "soma_lista_com_string", "entrada": [1, 2, "a", 4], "saida_esperada": None, "espera_excecao": ValueError}, # ❌ Teste de soma com lista contendo string não numérica (espera ValueError)
        {"nome": "soma_lista_com_float_sem_perda", "entrada": [1, 2, 3.0, 4], "saida_esperada": 10, "espera_excecao": None}, # ✅ Teste de soma com lista contendo float sem perda de precisão
        {"nome": "soma_lista_com_float_com_perda", "entrada": [1, 2, 3.5, 4], "saida_esperada": None, "espera_excecao": ValueError}, # ❌ Teste de soma com lista contendo float com perda de precisão (espera ValueError)
        {"nome": "soma_lista_com_none", "entrada": [1, 2, None, 4], "saida_esperada": None, "espera_excecao": ValueError}, # ❌ Teste de soma com lista contendo None (espera ValueError)
    ]

    for caso in casos_teste_soma: # 🔄 Executa cada caso de teste para a função sum_numbers
        resultado = executar_caso_teste(calculadora.sum_numbers, caso) # 🧪 Executa o caso de teste e obtém o resultado
        resultados_teste.append(resultado) # 📝 Adiciona o resultado do teste à lista de resultados

    casos_teste_media = [ # 🧪 Casos de teste para o método calculate_average (similar aos de soma, mas para média)
        {"nome": "media_inteiros_validos", "entrada": [1, 2, 3, 4], "saida_esperada": 2.5, "espera_excecao": None}, # ✅ Teste de média com inteiros válidos
        {"nome": "media_strings_numericas_validas", "entrada": ["5", "10", "15"], "saida_esperada": 10.0, "espera_excecao": None}, # ✅ Teste de média com strings numéricas válidas
        {"nome": "media_lista_vazia", "entrada": [], "saida_esperada": None, "espera_excecao": None}, # ✅ Teste de média com lista vazia (espera retorno None)
        {"nome": "media_tipo_invalido_string", "entrada": "nao_eh_lista", "saida_esperada": None, "espera_excecao": TypeError}, # ❌ Teste de média com tipo de entrada inválido (string, espera TypeError)
        {"nome": "media_lista_com_string", "entrada": [1, 2, "a", 4], "saida_esperada": None, "espera_excecao": ValueError}, # ❌ Teste de média com lista contendo string não numérica (espera ValueError)
        {"nome": "media_lista_com_float_sem_perda", "entrada": [1, 2, 3.0, 4], "saida_esperada": 2.5, "espera_excecao": None}, # ✅ Teste de média com lista contendo float sem perda de precisão
        {"nome": "media_lista_com_float_com_perda", "entrada": [1, 2, 3.5, 4], "saida_esperada": None, "espera_excecao": ValueError}, # ❌ Teste de média com lista contendo float com perda de precisão (espera ValueError)
        {"nome": "media_lista_com_none", "entrada": [1, 2, None, 4], "saida_esperada": None, "espera_excecao": ValueError}, # ❌ Teste de média com lista contendo None (espera ValueError)
        {"nome": "media_divisao_por_zero", "entrada": [0, 0, 0], "saida_esperada": 0.0, "espera_excecao": None}, # ✅ Teste de média com lista de zeros (espera média 0.0)
    ]

    for caso in casos_teste_media: # 🔄 Executa cada caso de teste para a função calculate_average
        resultado = executar_caso_teste(calculadora.calculate_average, caso) # 🧪 Executa o caso de teste e obtém o resultado
        resultados_teste.append(resultado) # 📝 Adiciona o resultado do teste à lista de resultados

    dados_log = {"timestamp_execucao_teste": datetime.datetime.now().isoformat(), "resultados_teste": resultados_teste} # 📝 Prepara os dados de log para serem salvos em arquivo JSON
    salvar_log_teste(dados_log) # 💾 Salva os dados de log em arquivo JSON

def executar_caso_teste(funcao_testar, caso_teste):
    """
    Executa um único caso de teste para uma função específica (sum_numbers ou calculate_average).

    Recebe a função a ser testada e um dicionário contendo os detalhes do caso de teste
    (nome, entrada, saída esperada, exceção esperada). Executa a função com a entrada fornecida
    e compara o resultado com a saída esperada, ou verifica se a exceção esperada é lançada.
    Registra o status do teste (PASSOU, FALHOU, ERRO) e detalhes adicionais em um dicionário
    de log para posterior análise.

    Args:
        funcao_testar (callable): A função da classe Numbers a ser testada (sum_numbers ou calculate_average).
        caso_teste (dict): Um dicionário contendo os parâmetros do caso de teste, incluindo:
            - "nome" (str): Nome descritivo do teste.
            - "entrada" (any): Dados de entrada para a função de teste.
            - "saida_esperada" (any): Valor esperado de retorno da função em caso de sucesso.
            - "espera_excecao" (Exception): Tipo de exceção esperada, se o teste esperar que uma exceção seja lançada.

    Returns:
        dict: Um dicionário contendo os resultados detalhados do caso de teste, incluindo:
            - "nome_teste" (str): Nome do teste.
            - "entrada" (any): Dados de entrada do teste.
            - "saida_esperada" (any): Saída esperada.
            - "excecao_esperada" (str): Nome da exceção esperada (se houver).
            - "saida_real" (any): Saída real obtida da função testada.
            - "status_teste" (str): Status do teste ("PASSOU", "FALHOU", "ERRO").
            - "excecao_real" (str, opcional): Nome da exceção real lançada (se aplicável).
            - "mensagem_excecao" (str, opcional): Mensagem da exceção lançada (se aplicável).
            - "mensagem_erro" (str, opcional): Mensagem de erro genérico (se ocorrer um erro inesperado).
    """
    nome_teste = caso_teste["nome"] # 🏷️ Nome do caso de teste
    dados_entrada = caso_teste["entrada"] # 📦 Dados de entrada para o teste
    saida_esperada = caso_teste["saida_esperada"] # 🎯 Saída esperada do teste
    excecao_esperada = caso_teste["espera_excecao"] # ⏳ Exceção esperada (se houver)

    entrada_log = {"nome_teste": nome_teste, "entrada": dados_entrada, "saida_esperada": saida_esperada, "excecao_esperada": excecao_esperada.__name__ if excecao_esperada else None} # 📝 Inicializa o dicionário de log para este caso de teste

    try: # 🔄 Bloco try-except para capturar exceções durante a execução do teste
        if excecao_esperada: # ⏳ Se o teste espera uma exceção
            with pytest.raises(excecao_esperada) as info_excecao: # 🛡️ Usa pytest.raises para verificar se a exceção esperada é lançada
                funcao_testar(dados_entrada) # 🧪 Executa a função de teste com os dados de entrada
            saida_real = None # 🔇 Define saida_real como None, pois espera-se uma exceção
            status_teste = "PASSOU" # ✅ Se a exceção esperada for lançada, o teste passa
            entrada_log["excecao_real"] = info_excecao.type.__name__ # 📝 Registra o nome da exceção real lançada
            entrada_log["mensagem_excecao"] = str(info_excecao.value) # 📝 Registra a mensagem da exceção lançada

        else: # ✅ Se o teste não espera uma exceção (espera um retorno bem-sucedido)
            saida_real = funcao_testar(dados_entrada) # 🧪 Executa a função de teste e obtém a saída real
            if saida_esperada is None: # 🎯 Caso esperado seja None (verifica se a saída real também é None)
                if saida_real is None: # ✅ Se a saída real for None, o teste passa
                    status_teste = "PASSOU" # ✅ Status do teste: PASSOU
                else: # ❌ Se a saída real não for None, mas esperava-se None, o teste falha
                    status_teste = "FALHOU" # ❌ Status do teste: FALHOU
                    entrada_log["saida_real"] = saida_real # 📝 Registra a saída real (incorreta)
            elif isinstance(saida_esperada, float): # 🔢 Caso esperado seja float (usa pytest.approx para comparação aproximada)
                if pytest.approx(saida_real) == saida_esperada: # ✅ Compara a saída real com a esperada usando pytest.approx para floats
                    status_teste = "PASSOU" # ✅ Status do teste: PASSOU
                else: # ❌ Se a saída real não for aproximadamente igual à esperada, o teste falha
                    status_teste = "FALHOU" # ❌ Status do teste: FALHOU
                    entrada_log["saida_real"] = saida_real # 📝 Registra a saída real (incorreta)
            else: # 🎯 Caso esperado seja de outro tipo (comparação direta)
                if saida_real == saida_esperada: # ✅ Compara a saída real com a esperada diretamente
                    status_teste = "PASSOU" # ✅ Status do teste: PASSOU
                else: # ❌ Se a saída real não for igual à esperada, o teste falha
                    status_teste = "FALHOU" # ❌ Status do teste: FALHOU
                    entrada_log["saida_real"] = saida_real # 📝 Registra a saída real (incorreta)

    except Exception as erro: # ❗ Captura qualquer exceção inesperada durante o teste (fora das exceções esperadas)
        status_teste = "ERRO" # ❗ Status do teste: ERRO (exceção inesperada)
        entrada_log["status_teste"] = status_teste # 📝 Registra o status do teste como ERRO
        entrada_log["mensagem_erro"] = str(erro) # 📝 Registra a mensagem do erro inesperado
        saida_real = None # 🔇 Define saida_real como None em caso de erro

    entrada_log["status_teste"] = status_teste # 📝 Garante que o status do teste seja sempre registrado no log
    return entrada_log # 📝 Retorna o dicionário de log completo para este caso de teste

if __name__ == "__main__":
    print("Iniciando testes da biblioteca calc_numbers...") # 💬 Mensagem de início dos testes no console
    executar_testes() # 🚀 Executa a função principal de testes
    print("Testes da biblioteca calc_numbers concluídos e resultados salvos em test_logs/") # 💬 Mensagem de conclusão e local dos logs no console