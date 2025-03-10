import os
import datetime

def document_project_structure(start_path="."):
    docs_dir = os.path.join(start_path, "docs")
    doc_file_path = os.path.join(docs_dir, "project_structure.txt")

    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"Diretório 'docs/' criado.")

    with open(doc_file_path, 'w', encoding='utf-8') as doc_file:
        doc_file.write("DOCUMENTAÇÃO AUTOMÁTICA DA ESTRUTURA DO PROJETO\n")
        doc_file.write("---------------------------------------------------\n")
        doc_file.write(f"Gerado por: {os.path.basename(__file__)}\n")
        doc_file.write("Data de Geração: {:%d/%m/%Y %H:%M:%S}\n".format(datetime.datetime.now()))
        doc_file.write("Codificação do Arquivo: UTF-8\n")
        doc_file.write("\nEstrutura de diretórios e arquivos a partir da raiz do projeto:\n\n")

        for root, dirs, files in os.walk(start_path):
            depth = root.replace(start_path, '').count(os.sep)
            indent = '  ' * depth
            doc_file.write(f"{indent}{os.path.basename(root)}/\n")

            sub_indent = '  ' * (depth + 1)
            for filename in files:
                if filename != os.path.basename(__file__):
                    doc_file.write(f"{sub_indent}{filename}\n")

        doc_file.write("\n---------------------------------------------------\n")
        doc_file.write("Fim da Documentação da Estrutura do Projeto.\n")
        doc_file.write("\nEste arquivo foi gerado automaticamente. Para atualizar a documentação,\n")
        doc_file.write("execute o script novamente: 'python {}'\n".format(os.path.basename(__file__)))
        doc_file.write("Certifique-se de que seu editor de texto/visualizador utilize UTF-8 para exibir corretamente os caracteres.\n")

    print(f"\nDocumentação da estrutura do projeto gerada com sucesso em: '{doc_file_path}' (Codificação: UTF-8)")


if __name__ == "__main__":
    print("Gerando documentação da estrutura do projeto (UTF-8)...")
    document_project_structure()
    print("\nProcesso concluído.")