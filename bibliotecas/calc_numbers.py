class Numbers:
    def __init__(self):
        pass

    def sum_numbers(self, numeros: any) -> int:
        try:
            validated_list = self._validate_integer_list(numeros, operation_name="soma")
            if not validated_list:
                raise ValueError("Erro de valor na operação de soma: A lista de números não pode estar vazia.")
            return sum(validated_list)
        except (TypeError, ValueError) as e:
            raise e

    def calculate_average(self, numeros: any) -> float | None:
        try:
            validated_list = self._validate_integer_list(numeros, operation_name="média")
            if not validated_list:
                return None
            return sum(validated_list) / len(validated_list)
        except (TypeError, ValueError) as e:
            raise e

    def _validate_input_list(self, data: any, operation_name: str) -> list:
        if not isinstance(data, list):
            raise TypeError(f"Erro de tipo na operação de {operation_name}: A entrada deve ser uma lista, mas foi fornecido '{type(data).__name__}'.")
        if data is None:
            raise ValueError(f"Erro de valor na operação de {operation_name}: A lista de números não pode ser None.")
        if not data and operation_name == "soma":
            raise ValueError(f"Erro de valor na operação de {operation_name}: A lista de números não pode estar vazia.")
        if not data and operation_name == "média":
            return []
        return data

    def _validate_integer_list(self, data: any, operation_name: str) -> list[int]:
        try:
            validated_list = self._validate_input_list(data, operation_name)
        except (TypeError, ValueError) as e:
            raise e

        if not validated_list and operation_name == "média":
            return []

        integer_list = []
        for index, item in enumerate(validated_list):
            if item is None:
                raise ValueError(f"Erro de valor na operação de {operation_name}: Elemento na posição {index+1} não pode ser None.")
            if isinstance(item, int):
                integer_list.append(item)
            elif isinstance(item, (float, str)):
                try:
                    integer_item = int(float(item))
                    if integer_item != float(item):
                        raise ValueError(f"Erro de valor na operação de {operation_name}: Elemento na posição {index+1} ('{item}') não é um inteiro válido e a conversão resultaria em perda de informação. Forneça apenas inteiros.")
                    integer_list.append(integer_item)
                except ValueError:
                    raise ValueError(f"Erro de valor na operação de {operation_name}: Elemento na posição {index+1} ('{item}') não é um inteiro válido e não pode ser convertido para inteiro.")
            else:
                raise ValueError(f"Erro de valor na operação de {operation_name}: Elemento na posição {index+1} ('{item}') não é um inteiro válido. Tipo encontrado: '{type(item).__name__}'.")
        return integer_list