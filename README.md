# B3 Viewer

Este é um projeto em Django que faz uso de modelos, visualizações e autenticação de usuários. Ele permite que os usuários monitorem o preço de ações e recebam notificações quando os preços atingirem um determinado limite.

## Importante!!

1. Foi usada a API do Yahoo Finances para a aquisição de dados de ações.
2. Para rodar o projeto, é necessário configurar o seu serviço de email no arquivo .env.

## Instalação

1. Clone o repositório: `git clone https://github.com/erikgna/inoa.git`
2. Crie um ambiente virtual com `python -m venv <env_name>`
3. Acesse o ambiente virtual com `source env/bin/activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Execute as migrações do banco de dados: `python manage.py migrate`

## Uso

1. Inicie o servidor local: `python manage.py runserver`
2. Acesse a página inicial em http://localhost:8000/
3. Faça login com suas credenciais ou crie uma conta se ainda não tiver uma
4. Adicione ações para monitorar seus preços
5. Receba notificações quando os preços atingirem os limites definidos

## Docker

Para executar o aplicativo usando o arquivo `docker-compose.yml` fornecido, siga as seguintes etapas:

1. Certifique-se de ter o Docker e o Docker Compose instalados em sua máquina.
2. Execute o seguinte comando para iniciar o contêiner Docker: `docker compose up`.
3. O servidor deve agora estar em execução no endereço `http://localhost:8000/`.
