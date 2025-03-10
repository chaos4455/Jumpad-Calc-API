# CHANGELOG

## v0.1 - 2025-03-10

**🎉 Versão Inicial do Projeto Jumpad API**

Esta versão marca o lançamento inicial do projeto Jumpad API, uma API RESTful focada em operações matemáticas básicas, com ênfase em segurança, documentação e boas práticas de desenvolvimento.

**✨ Principais Novidades e Funcionalidades:**

*   **🚀 API RESTful Funcional:**
    *   Implementação completa de uma API RESTful utilizando o framework FastAPI em Python.
    *   Endpoints para operações de **soma** (`/somar`) e **cálculo da média** (`/calcular_media`) de vetores de números inteiros, acessíveis via método `POST` e protegidos por autenticação JWT.
    *   Endpoint público de **saúde da API** (`/saude`) para verificação do status operacional.
    *   Endpoints de **autenticação JWT** (`/token_admin`, `/token_tester`) para geração de tokens de acesso.

*   **🔐 Segurança Implementada:**
    *   **Autenticação JWT (JSON Web Tokens):**  Segurança reforçada com autenticação baseada em tokens JWT para proteger os endpoints de operações matemáticas, garantindo que apenas usuários autorizados possam acessá-los.
    *   **HTTPS Habilitado:** Comunicação segura através do protocolo HTTPS, com geração automática de certificados autoassinados para facilitar o desenvolvimento e testes locais.
    *   **CORS (Cross-Origin Resource Sharing):** Configuração de CORS para restringir o acesso à API apenas a origens permitidas (localhost por padrão), aumentando a segurança contra ataques cross-site.

*   **📚 Documentação Abrangente e Interativa:**
    *   **Swagger UI Integrado:** Documentação interativa da API gerada automaticamente e disponível via Swagger UI, permitindo explorar os endpoints e realizar testes diretamente no navegador.
    *   **ReDoc Implementado:** Documentação alternativa e elegante gerada com ReDoc, oferecendo uma visualização clara e profissional da API.

*   **🧪 Testes Automatizados Robustos:**
    *   **Testes Unitários com Pytest:** Implementação de testes unitários abrangentes para a biblioteca `bibliotecas/calc_numbers.py` utilizando o framework `pytest`, garantindo a corretude e robustez da lógica de cálculos.
    *   **Testes de Integração com Unittest:** Criação de testes de integração da API RESTful utilizando `unittest` e `requests`, validando o funcionamento dos endpoints, a segurança JWT, e a validação de dados.
    *   **Logs Detalhados de Testes:** Geração de logs em formato JSON para os testes automatizados, facilitando a análise e o rastreamento de resultados.

*   **🐳 Preparação para DevOps (Templates Iniciais):**
    *   **Dockerfile Base:** Inclusão de um Dockerfile inicial para facilitar a futura conteinerização da API com Docker.
    *   **Templates Kubernetes:** Criação de templates YAML para Kubernetes (Service, Deployment, ConfigMap, Secret), oferecendo um ponto de partida para o deploy da API em clusters Kubernetes (templates ainda não funcionais e precisam de validação).
    *   **Templates GitHub Actions:** Implementação de templates YAML para workflows do GitHub Actions, visando automatizar os processos de CI/CD (build, teste e deploy) do projeto (workflows também em estágio inicial e não totalmente funcionais).

**🛠️ Como Foi Feito:**

*   **Framework FastAPI:** Utilizado para construir a API RESTful de forma rápida, eficiente e com recursos robustos de documentação e validação.
*   **Python 3.11:** Linguagem de programação principal, garantindo legibilidade, facilidade de manutenção e acesso a um vasto ecossistema de bibliotecas.
*   **Bibliotecas de Segurança:** Utilização de `python-jose[cryptography]` e `cryptography` para implementar a autenticação JWT e garantir a segurança da API.
*   **Pydantic:** Empregado para a validação de dados de requisição e resposta, e para a definição de schemas para a documentação da API.
*   **Pytest e Unittest:** Frameworks de teste `pytest` e `unittest` foram utilizados para criar suítes de testes unitários e de integração, respectivamente, garantindo a qualidade do código.
*   **Logging:** Sistema de logging configurado para fornecer logs coloridos no console e logs estruturados em JSON para análise e monitoramento.

**📝 Notas:**

*   Esta versão inicial (v0.1) representa uma base sólida para o projeto Jumpad API.
*   Os templates Dockerfile, Kubernetes Manifests e GitHub Actions Workflows são **esboços iniciais** e **não estão totalmente funcionais ou validados**.
*   Melhorias e novas funcionalidades serão adicionadas em versões futuras, incluindo a finalização dos templates CI/CD, a implementação de Rate Limiting, monitoramento avançado, e a possível expansão para outras operações matemáticas.

**🚀 Próximos Passos:**

*   Validação e finalização dos templates Dockerfile e Kubernetes.
*   Implementação de um pipeline de CI/CD automatizado utilizando GitHub Actions.
*   Exploração de funcionalidades adicionais e melhorias de performance.
*   Coleta de feedback e identificação de novas demandas e requisitos.