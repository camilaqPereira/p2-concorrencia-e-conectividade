#versão do python utilizada
FROM python:3.12

#deixa exposta a porta 8000
EXPOSE 8000

#diretorio de trabalho
WORKDIR /serverSide

#copia tudo apatir de um diretorio a cima para dentro da pasta  do container
COPY ../. .

#instalar dependencias do python
RUN pip install networkx
RUN pip install requests
RUN pip install flask
RUN pip install flask_restful
RUN pip install flask_cors


#rodar o servidor na inicialização do container
CMD ["python", "-m", "serverSide.server"]