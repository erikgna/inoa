# Define a imagem base
FROM python:3.9

# Define a diretório de trabalho na imagem
WORKDIR /app

# Copia o arquivo de requisitos para dentro da imagem
COPY requirements.txt .

# Instala as dependências
RUN pip install -r requirements.txt

# Copia o restante dos arquivos para dentro da imagem
COPY . .

# Define as variáveis de ambiente necessárias para a aplicação Django
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PYTHONUNBUFFERED=1

# Expõe a porta 8000 da imagem para o host
EXPOSE 8000

# Define o comando padrão que será executado quando a imagem for iniciada
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
