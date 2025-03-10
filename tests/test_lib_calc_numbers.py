import sys
import os
import json
import datetime
import pytest
from bibliotecas.calc_numbers import Numbers

DIRETORIO_LOGS_TESTE = "test_logs"
if not os.path.exists(DIRETORIO_LOGS_TESTE):
    os.makedirs(DIRETORIO_LOGS_TESTE)

def obter_proximo_nome_arquivo_log():
    contador_logs = 1
    while True:
        nome_arquivo_log = os.path.join(DIRETORIO_LOGS_TESTE, f"log_teste_{contador_logs}.json")
        if not os.path.exists(nome_arquivo_log):
            return nome_arquivo_log
        contador_logs += 1

def salvar_log_teste(dados_log):
    nome_arquivo_log = obter_proximo_nome_arquivo_log()
    with open(nome_arquivo_log, 'w', encoding='utf-8') as arquivo:
        json.dump(dados_log, arquivo, indent=4, ensure_ascii=False)
    print(f"Resultados dos testes salvos em: {nome_arquivo_log}")


def executar_testes():
    calculadora = Numbers()
    resultados_teste = []

    casos_teste_soma = [
        {"nome": "soma_inteiros_validos", "entrada": [1, 2, 3, 4], "saida_esperada": 10, "espera_excecao": None},
        {"nome": "soma_strings_numericas_validas", "entrada": ["5", "10", "15"], "saida_esperada": 30, "espera_excecao": None},
        {"nome": "soma_lista_vazia", "entrada": [], "saida_esperada": None, "espera_excecao": ValueError},
        {"nome": "soma_tipo_invalido_string", "entrada": "nao_eh_lista", "saida_esperada": None, "espera_excecao": TypeError},
        {"nome": "soma_lista_com_string", "entrada": [1, 2, "a", 4], "saida_esperada": None, "espera_excecao": ValueError},
        {"nome": "soma_lista_com_float_sem_perda", "entrada": [1, 2, 3.0, 4], "saida_esperada": 10, "espera_excecao": None},
        {"nome": "soma_lista_com_float_com_perda", "entrada": [1, 2, 3.5, 4], "saida_esperada": None, "espera_excecao": ValueError},
        {"nome": "soma_lista_com_none", "entrada": [1, 2, None, 4], "saida_esperada": None, "espera_excecao": ValueError},
    ]

    for caso in casos_teste_soma:
        resultado = executar_caso_teste(calculadora.sum_numbers, caso)
        resultados_teste.append(resultado)

    casos_teste_media = [
        {"nome": "media_inteiros_validos", "entrada": [1, 2, 3, 4], "saida_esperada": 2.5, "espera_excecao": None},
        {"nome": "media_strings_numericas_validas", "entrada": ["5", "10", "15"], "saida_esperada": 10.0, "espera_excecao": None},
        {"nome": "media_lista_vazia", "entrada": [], "saida_esperada": None, "espera_excecao": None},
        {"nome": "media_tipo_invalido_string", "entrada": "nao_eh_lista", "saida_esperada": None, "espera_excecao": TypeError},
        {"nome": "media_lista_com_string", "entrada": [1, 2, "a", 4], "saida_esperada": None, "espera_excecao": ValueError},
        {"nome": "media_lista_com_float_sem_perda", "entrada": [1, 2, 3.0, 4], "saida_esperada": 2.5, "espera_excecao": None},
        {"nome": "media_lista_com_float_com_perda", "entrada": [1, 2, 3.5, 4], "saida_esperada": None, "espera_excecao": ValueError},
        {"nome": "media_lista_com_none", "entrada": [1, 2, None, 4], "saida_esperada": None, "espera_excecao": ValueError},
        {"nome": "media_divisao_por_zero", "entrada": [0, 0, 0], "saida_esperada": 0.0, "espera_excecao": None},
    ]

    for caso in casos_teste_media:
        resultado = executar_caso_teste(calculadora.calculate_average, caso)
        resultados_teste.append(resultado)

    dados_log = {"timestamp_execucao_teste": datetime.datetime.now().isoformat(), "resultados_teste": resultados_teste}
    salvar_log_teste(dados_log)


def executar_caso_teste(funcao_testar, caso_teste):
    nome_teste = caso_teste["nome"]
    dados_entrada = caso_teste["entrada"]
    saida_esperada = caso_teste["saida_esperada"]
    excecao_esperada = caso_teste["espera_excecao"]

    entrada_log = {"nome_teste": nome_teste, "entrada": dados_entrada, "saida_esperada": saida_esperada, "excecao_esperada": excecao_esperada.__name__ if excecao_esperada else None}

    try:
        if excecao_esperada:
            with pytest.raises(excecao_esperada) as info_excecao:
                funcao_testar(dados_entrada)
            saida_real = None
            status_teste = "PASSOU"
            entrada_log["excecao_real"] = info_excecao.type.__name__
            entrada_log["mensagem_excecao"] = str(info_excecao.value)

        else:
            saida_real = funcao_testar(dados_entrada)
            if saida_esperada is None:
                if saida_real is None:
                    status_teste = "PASSOU"
                else:
                    status_teste = "FALHOU"
                    entrada_log["saida_real"] = saida_real
            elif isinstance(saida_esperada, float):
                if pytest.approx(saida_real) == saida_esperada:
                    status_teste = "PASSOU"
                else:
                    status_teste = "FALHOU"
                    entrada_log["saida_real"] = saida_real
            else:
                if saida_real == saida_esperada:
                    status_teste = "PASSOU"
                else:
                    status_teste = "FALHOU"
                    entrada_log["saida_real"] = saida_real

    except Exception as erro:
        status_teste = "ERRO"
        entrada_log["status_teste"] = status_teste
        entrada_log["mensagem_erro"] = str(erro)
        saida_real = None

    entrada_log["status_teste"] = status_teste
    return entrada_log


if __name__ == "__main__":
    print("Iniciando testes da biblioteca calc_numbers...")
    executar_testes()
    print("Testes da biblioteca calc_numbers concluídos e resultados salvos em test_logs/")