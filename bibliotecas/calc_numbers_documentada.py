# -*- coding: utf-8 -*-
"""
Biblioteca para Operações Numéricas Seguras (Classe Numbers)

Esta biblioteca Python fornece a classe `Numbers` que encapsula métodos para realizar
operações matemáticas básicas, como soma e média, em listas de números inteiros.
A classe `Numbers` foi projetada com foco na robustez e segurança, incluindo
validações rigorosas dos dados de entrada para prevenir erros e comportamentos
inesperados.

A classe `Numbers` oferece as seguintes funcionalidades principais:

    - Soma de listas de números inteiros: O método `sum_numbers` calcula a soma de todos os
      números em uma lista fornecida, realizando validações para garantir que a entrada
      seja uma lista de inteiros válidos.

    - Cálculo da média de listas de números inteiros: O método `calculate_average` calcula a
      média aritmética de uma lista de números inteiros, também com validação de entrada.
      Em caso de lista vazia, retorna `None`.

    - Validação de entrada: Métodos internos (`_validate_input_list` e `_validate_integer_list`)
      são utilizados para assegurar que as listas de entrada sejam do tipo correto (list) e
      contenham apenas números inteiros válidos, ou valores que possam ser convertidos para
      inteiros sem perda de informação.

A biblioteca `Numbers` é ideal para aplicações que necessitam de operações matemáticas
simples, porém com alta confiabilidade e tratamento adequado de erros e dados de entrada
potencialmente inválidos.

Classe:
    Numbers: Classe que implementa as operações de soma e média com validação de entrada.

Para utilizar esta biblioteca, basta importar a classe `Numbers` e instanciá-la.
Em seguida, pode-se chamar os métodos `sum_numbers` e `calculate_average` passando
uma lista de números como argumento.

Exemplo de uso:
    from bibliotecas.calc_numbers import Numbers

    calculadora = Numbers()
    lista_de_numeros = [1, 2, 3, 4, 5]

    soma = calculadora.sum_numbers(lista_de_numeros)
    print(f"A soma dos números é: {soma}")

    media = calculadora.calculate_average(lista_de_numeros)
    print(f"A média dos números é: {media}")

Criado por: Elias Andrade
Data de Criação: 10 de Março de 2025
"""

class Numbers:
    """
    Classe para realizar operações matemáticas em listas de números inteiros com validação de entrada.

    A classe `Numbers` fornece métodos para calcular a soma e a média de listas de números inteiros,
    incluindo validações robustas para garantir que os dados de entrada sejam válidos e para
    prevenir erros durante as operações.

    Métodos:
        __init__(): Inicializa uma instância da classe Numbers.
        sum_numbers(numeros: any) -> int: Calcula a soma de uma lista de números inteiros.
        calculate_average(numeros: any) -> float | None: Calcula a média de uma lista de números inteiros.
        _validate_input_list(data: any, operation_name: str) -> list: Valida se a entrada é uma lista. (Método interno)
        _validate_integer_list(data: any, operation_name: str) -> list[int]: Valida se a lista contém apenas inteiros válidos. (Método interno)
    """
    def __init__(self):
        """
        Inicializa uma nova instância da classe Numbers.

        Atualmente, o método de inicialização não realiza nenhuma ação específica.
        Ele serve principalmente como um construtor padrão para a classe.
        """
        pass

    def sum_numbers(self, numeros: any) -> int:
        """
        Calcula a soma de uma lista de números inteiros.

        Este método recebe uma lista (ou um tipo de dado compatível) e calcula a soma de todos os
        elementos numéricos presentes na lista. Ele realiza validações para garantir que a entrada
        seja uma lista válida e que contenha apenas números inteiros ou valores que possam ser
        convertidos para inteiros sem perda de informação.

        Args:
            numeros (any): A lista de números a serem somados. Pode ser uma lista Python padrão
                           ou qualquer tipo de dado que possa ser validado como uma lista de inteiros.

        Returns:
            int: A soma de todos os números inteiros na lista de entrada.

        Raises:
            TypeError: Se a entrada `numeros` não for do tipo lista.
            ValueError: Se a lista de números for None ou vazia, ou se contiver elementos que não
                        podem ser convertidos para inteiros válidos sem perda de informação.
        """
        try:
            validated_list = self._validate_integer_list(numeros, operation_name="soma")
            if not validated_list:
                raise ValueError("Erro de valor na operação de soma: A lista de números não pode estar vazia.")
            return sum(validated_list)
        except (TypeError, ValueError) as e:
            raise e

    def calculate_average(self, numeros: any) -> float | None:
        """
        Calcula a média aritmética de uma lista de números inteiros.

        Este método recebe uma lista (ou um tipo de dado compatível) e calcula a média dos
        elementos numéricos presentes na lista. Ele realiza validações para garantir que a
        entrada seja uma lista válida e que contenha apenas números inteiros ou valores que
        possam ser convertidos para inteiros sem perda de informação.

        Se a lista de entrada for vazia, o método retorna `None`, pois a média de uma lista
        vazia é indefinida ou pode ser considerada como não aplicável em certos contextos.

        Args:
            numeros (any): A lista de números para calcular a média. Pode ser uma lista Python
                           padrão ou qualquer tipo de dado que possa ser validado como uma lista
                           de inteiros.

        Returns:
            float | None: A média dos números inteiros na lista de entrada, como um número de ponto flutuante.
                          Retorna `None` se a lista de entrada for vazia.

        Raises:
            TypeError: Se a entrada `numeros` não for do tipo lista.
            ValueError: Se a lista de números for None, ou se contiver elementos que não podem
                        ser convertidos para inteiros válidos sem perda de informação.
        """
        try:
            validated_list = self._validate_integer_list(numeros, operation_name="média")
            if not validated_list:
                return None
            return sum(validated_list) / len(validated_list)
        except (TypeError, ValueError) as e:
            raise e

    def _validate_input_list(self, data: any, operation_name: str) -> list:
        """
        Valida se a entrada fornecida é uma lista Python. (Método interno)

        Este método interno verifica se o argumento `data` é do tipo lista.
        Se não for, levanta uma exceção TypeError. Também verifica se a lista é `None`,
        levantando ValueError neste caso. Para a operação de "soma", também verifica se a lista está vazia,
        levantando ValueError se for o caso. Para a operação de "média", listas vazias são permitidas
        e retornadas sem levantar exceção.

        Este método é destinado para uso interno na classe `Numbers` para validação de dados de entrada
        antes de realizar operações matemáticas.

        Args:
            data (any): Os dados de entrada a serem validados. Espera-se que seja uma lista.
            operation_name (str): O nome da operação que está sendo validada (e.g., "soma", "média").
                                   Usado para mensagens de erro mais contextuais.

        Returns:
            list: Retorna a lista de entrada original se a validação for bem-sucedida.

        Raises:
            TypeError: Se `data` não for do tipo lista.
            ValueError: Se `data` for None ou se for uma lista vazia e a `operation_name` for "soma".
        """
        if not isinstance(data, list):
            raise TypeError(f"Erro de tipo na operação de {operation_name}: A entrada deve ser uma lista, mas foi fornecido '{type(data).__name__}'.")
        if data is None:
            raise ValueError(f"Erro de valor na operação de {operation_name}: A lista de números não pode ser None.")
        if not data and operation_name == "soma":
            raise ValueError(f"Erro de valor na operação de {operation_name}: A lista de números não pode estar vazia.")
        if not data and operation_name == "média":
            return [] # Listas vazias são permitidas para a média, retorna lista vazia
        return data

    def _validate_integer_list(self, data: any, operation_name: str) -> list[int]:
        """
        Valida se os elementos de uma lista são números inteiros válidos. (Método interno)

        Este método interno primeiro utiliza `_validate_input_list` para garantir que a entrada
        seja uma lista válida. Em seguida, itera sobre cada elemento da lista para verificar se são
        números inteiros ou se podem ser convertidos para inteiros sem perda de informação.

        Se algum elemento não for um inteiro válido ou não puder ser convertido para inteiro sem perda,
        um ValueError é levantado. Valores `None` dentro da lista também levantam ValueError.

        Este método é destinado para uso interno na classe `Numbers` para garantir que as listas de
        números contenham apenas inteiros válidos antes de realizar operações matemáticas.

        Args:
            data (any): Os dados de entrada a serem validados. Espera-se que seja uma lista de números.
            operation_name (str): O nome da operação que está sendo validada (e.g., "soma", "média").
                                   Usado para mensagens de erro mais contextuais.

        Returns:
            list[int]: Retorna uma nova lista contendo os elementos convertidos para inteiros (se necessário)
                       se todos os elementos forem válidos.

        Raises:
            TypeError: Se a entrada `data` não for do tipo lista (levantado por `_validate_input_list`).
            ValueError: Se a lista de números for None ou vazia (para a operação de "soma"), ou se
                        contiver elementos que não são inteiros válidos ou não podem ser convertidos
                        para inteiros sem perda de informação, ou se contiver elementos `None`.
        """
        try:
            validated_list = self._validate_input_list(data, operation_name) # Valida se é uma lista usando _validate_input_list
        except (TypeError, ValueError) as e:
            raise e # Re-levanta exceções de tipo ou valor encontradas na validação inicial

        if not validated_list and operation_name == "média":
            return [] # Listas vazias são permitidas para a média, retorna lista vazia

        integer_list = [] # Lista para armazenar os inteiros validados
        for index, item in enumerate(validated_list): # Itera sobre cada item na lista validada
            if item is None: # Verifica se o item é None
                raise ValueError(f"Erro de valor na operação de {operation_name}: Elemento na posição {index+1} não pode ser None.")
            if isinstance(item, int): # Se o item já for um inteiro
                integer_list.append(item) # Adiciona diretamente à lista de inteiros
            elif isinstance(item, (float, str)): # Se o item for float ou string, tenta converter para inteiro
                try:
                    integer_item = int(float(item)) # Converte para float primeiro para lidar com strings numéricas como "3.0"
                    if integer_item != float(item): # Verifica se houve perda de informação na conversão para inteiro
                        raise ValueError(f"Erro de valor na operação de {operation_name}: Elemento na posição {index+1} ('{item}') não é um inteiro válido e a conversão resultaria em perda de informação. Forneça apenas inteiros.")
                    integer_list.append(integer_item) # Adiciona o inteiro convertido à lista
                except ValueError: # Captura erros se a conversão para float ou int falhar
                    raise ValueError(f"Erro de valor na operação de {operation_name}: Elemento na posição {index+1} ('{item}') não é um inteiro válido e não pode ser convertido para inteiro.")
            else: # Se o item não for nem int, float ou string
                raise ValueError(f"Erro de valor na operação de {operation_name}: Elemento na posição {index+1} ('{item}') não é um inteiro válido. Tipo encontrado: '{type(item).__name__}'.")
        return integer_list # Retorna a lista de inteiros validados