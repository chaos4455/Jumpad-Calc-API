import os
import sqlite3
import chardet
import datetime

# Define o nome da pasta 'docs' e o caminho completo para o arquivo de saída
DOCS_FOLDER = "docs"
OUTPUT_FILE = os.path.join(DOCS_FOLDER, "docproject.txt")
SAMPLE_SIZE = 3
LARGE_TABLE_THRESHOLD = 100

def detect_encoding(filepath):
    try:
        with open(filepath, 'rb') as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            return result['encoding']
    except Exception:
        return 'utf-8'

def get_file_info(filepath):
    size_bytes = os.path.getsize(filepath)
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024

    line_count = 0
    try:
        encoding = detect_encoding(filepath)
        with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
            for line in f:
                line_count += 1
    except Exception as e:
        print(f"Aviso: Erro ao contar linhas de '{filepath}': {e}")
        line_count = -1

    return {
        "tamanho_bytes": size_bytes,
        "tamanho_kb": f"{size_kb:.2f}",
        "tamanho_mb": f"{size_mb:.2f}",
        "numero_linhas": line_count
    }

def get_file_content_bruto(filepath):
    try:
        encoding = detect_encoding(filepath)
        with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Aviso: Erro ao ler conteúdo de '{filepath}': {e}")
        return "[ERRO AO LER CONTEÚDO]"

def analyze_sqlite_db(filepath, doc_file):
    conn = None
    try:
        conn = sqlite3.connect(filepath)
        cursor = conn.cursor()

        doc_file.write("\n" + "="*80 + "\n")
        doc_file.write(f"  💾 Banco de Dados SQLite: {filepath}\n")
        doc_file.write("="*80 + "\n")

        db_size_bytes = os.path.getsize(filepath)
        db_size_kb = db_size_bytes / 1024
        db_size_mb = db_size_kb / 1024

        doc_file.write(f"  Tamanho: {db_size_mb:.2f} MB ({db_size_kb:.2f} KB, {db_size_bytes} bytes)\n")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if tables:
            doc_file.write(f"\n  Tabelas:\n")
            for table_name_tuple in tables:
                table_name = table_name_tuple[0]
                doc_file.write(f"\n    🗂️ Tabela: {table_name}\n")

                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns_info = cursor.fetchall()
                if columns_info:
                    doc_file.write(f"    Colunas:\n")
                    doc_file.write("    " + "-"*74 + "\n")
                    doc_file.write(f"    | {'ID':<4} | {'Nome':<20} | {'Tipo':<15} | {'Não Nulo?':<10} | {'Padrão':<10} | {'PK':<3} |\n")
                    doc_file.write("    " + "-"*74 + "\n")

                    for col_info in columns_info:
                        cid, name, type_str, notnull, dflt_value, pk = col_info
                        doc_file.write(f"    | {cid:<4} | {name:<20} | {type_str:<15} | {'Sim' if notnull else 'Não':<10} | {str(dflt_value):<10} | {'Sim' if pk else 'Não':<3} |\n")
                    doc_file.write("    " + "-"*74 + "\n")


                cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
                row_count = cursor.fetchone()[0]
                doc_file.write(f"    Número de Registros: {row_count}\n")

                if row_count > 0:
                    doc_file.write(f"    Amostra de Dados:\n")

                    doc_file.write(f"      Topo ({SAMPLE_SIZE} registros):\n")
                    cursor.execute(f"SELECT * FROM '{table_name}' LIMIT {SAMPLE_SIZE}")
                    top_rows = cursor.fetchall()
                    if top_rows:
                        header_row = [col_info[1] for col_info in columns_info]
                        doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")
                        doc_file.write("      | " + " | ".join([f'{header:<20}' for header in header_row]) + " |\n")
                        doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")

                        for row in top_rows:
                            doc_file.write("      | " + " | ".join([f'{str(item):<20}' for item in row]) + " |\n")
                        doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")


                    doc_file.write(f"      Fundo ({SAMPLE_SIZE} registros):\n")
                    cursor.execute(f"SELECT * FROM '{table_name}' ORDER BY ROWID DESC LIMIT {SAMPLE_SIZE}")
                    bottom_rows = cursor.fetchall()
                    if bottom_rows:
                        doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")
                        doc_file.write("      | " + " | ".join([f'{header:<20}' for header in header_row]) + " |\n")
                        doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")
                        for row in bottom_rows:
                            doc_file.write("      | " + " | ".join([f'{str(item):<20}' for item in row]) + " |\n")
                        doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")

                    if row_count > LARGE_TABLE_THRESHOLD:
                        doc_file.write(f"      Meio ({SAMPLE_SIZE} registros):\n")
                        offset = row_count // 2 - (SAMPLE_SIZE // 2) if row_count > SAMPLE_SIZE else 0
                        if offset < 0: offset = 0
                        cursor.execute(f"SELECT * FROM '{table_name}' LIMIT {SAMPLE_SIZE} OFFSET {offset}")
                        middle_rows = cursor.fetchall()
                        if middle_rows:
                            doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")
                            doc_file.write("      | " + " | ".join([f'{header:<20}' for header in header_row]) + " |\n")
                            doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")
                            for row in middle_rows:
                                doc_file.write("      | " + " | ".join([f'{str(item):<20}' for item in row]) + " |\n")
                            doc_file.write("      " + "-"*(len(header_row) * 22 + 6) + "\n")


        else:
            doc_file.write(f"  Nenhuma tabela encontrada neste banco de dados.\n")


    except sqlite3.Error as e:
        doc_file.write(f"Erro ao analisar banco de dados SQLite '{filepath}': {e}\n")
    finally:
        if conn:
            conn.close()

def main():
    root_dir = "."
    print("⚙️ Iniciando Análise do Projeto ⚙️")

    # Cria a pasta 'docs' se ela não existir
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as doc_file:
        doc_file.write(f"# Documentação do Projeto\n\n")
        doc_file.write(f"Este documento foi gerado automaticamente pelo script `documentador_projeto.py`.\n\n")
        doc_file.write(f"Data de Geração: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        doc_file.write(f"Diretório Raiz: {os.path.abspath(root_dir)}\n\n")
        doc_file.write("="*80 + "\n")

        for root, dirs, files in os.walk(root_dir):
            for dir_name in dirs:
                folder_path = os.path.join(root, dir_name)
                doc_file.write(f"\n📂 Pasta: {folder_path}\n")

            for file_name in files:
                filepath = os.path.join(root, file_name)
                file_ext = file_name.lower().split('.')[-1]

                doc_file.write(f"\n📄 Arquivo: {filepath}\n")

                file_info = get_file_info(filepath)
                doc_file.write(f"  Tamanho: {file_info['tamanho_mb']} MB ({file_info['tamanho_kb']} KB, {file_info['tamanho_bytes']} bytes)\n")
                doc_file.write(f"  Número de Linhas: {file_info['numero_linhas']}\n")

                if file_ext in ('py', 'txt', 'js', 'html', 'css', 'java', 'c', 'cpp', 'h', 'sh', 'sql', 'md'):
                    doc_file.write(f"\n  Código Fonte:\n")
                    code_content = get_file_content_bruto(filepath)
                    doc_file.write(code_content)
                else:
                    doc_file.write(f"  Conteúdo não textual ou extensão não suportada para visualização do código fonte.\n")

                if file_ext in ('db', 'sqlite', 'sqlite3'):
                    analyze_sqlite_db(filepath, doc_file)

    print("✅ Documentação Gerada com Sucesso! ✅")
    print(f"Arquivo de documentação salvo em: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()