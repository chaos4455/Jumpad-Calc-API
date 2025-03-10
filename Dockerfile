# Dockerfile para o projeto jumpad - API de Matemática Segura
# Este Dockerfile NÃO ESTÁ FUNCIONAL COMPLETAMENTE e será finalizado em uma versão futura.
# NÃO FOI VALIDADO completamente e pode precisar de ajustes.
# Criado por: Elias Andrade - Maringá Paraná - 10/03/2025

# Imagem base: Ubuntu 22.04 LTS
FROM ubuntu:22.04

# Informações do autor (opcional)
LABEL author="Elias Andrade - Maringá Paraná"
LABEL date="2025-03-10"

# Atualizar o sistema e instalar pacotes essenciais
RUN apt-get update && apt-get upgrade -y

# Instalar Python 3.11 e pip
RUN apt-get install -y python3.11 python3.11-venv python3-pip

# Definir Python 3.11 como padrão
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Criar diretório para o projeto dentro do container
WORKDIR /app

# Copiar os arquivos do projeto para o diretório /app no container
COPY . /app/

# Criar um ambiente virtual Python
RUN python3.11 -m venv venv
# Ativar o ambiente virtual
RUN source /app/venv/bin/activate

# Instalar as dependências do projeto a partir do requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instalar UFW (Firewall)
RUN apt-get install -y ufw

# Definir regras do UFW (permitir acesso na porta 8882 - porta da API)
RUN ufw allow 8882/tcp
# Habilitar o UFW (cuidado! - em produção, valide as regras antes de habilitar)
RUN ufw enable

# Criar usuário 'server' com senha 'admin-jump@d!!!'
RUN useradd -m server
RUN echo "server:admin-jump@d!!!" | chpasswd

# Expor a porta 8882 para acesso externo
EXPOSE 8882

# Definir o usuário 'server' para executar a aplicação (mais seguro)
USER server

# Comando para executar a API quando o container iniciar
CMD ["/app/venv/bin/uvicorn", "app.API-main-server-prod:app", "--host", "0.0.0.0", "--port", "8882", "--ssl-certfile", "/app/credentials/certificado.pem", "--ssl-keyfile", "/app/credentials/chave.pem"]

# Instruções adicionais importantes:
# 1. Este Dockerfile assume que a estrutura de pastas e arquivos do projeto está correta
#    e que os caminhos para certificados no comando CMD estão corretos.
# 2. A senha do usuário 'server' está hardcoded no Dockerfile, o que não é recomendado para produção.
#    Em produção, utilize mecanismos mais seguros para gerenciar senhas e credenciais.
# 3. As regras do UFW são básicas (permitir porta 8882). Em produção, configure regras mais robustas
#    e restrinja o acesso conforme necessário.
# 4. A geração de certificados autoassinados e credenciais padrão dentro do container
#    pode não ser ideal para produção. Considere montar volumes externos para fornecer esses arquivos
#    de forma mais segura e configurável.
# 5. Este Dockerfile é um ponto de partida e precisa ser testado e ajustado para o ambiente de produção real.