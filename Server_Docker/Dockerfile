#versão do python utilizada
FROM python:3.12

#deixa exposta a porta 8000
EXPOSE 8000

#diretorio de trabalho
WORKDIR /serverSide

#copia tudo apatir de um diretorio a cima para dentro da pasta  do container
COPY ../. .

#instalar dependencias do python
RUN pip install scipy

#rodar o servidor na inicialização do container
CMD ["python", "-m", "serverSide.server"]