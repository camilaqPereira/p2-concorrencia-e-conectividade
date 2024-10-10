import socket
host = ''
port = 5000
addr = (host, port)

#cria um socket ipv4  tcp/ip
serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#encerra o socket caso o programa seja encerrado
serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#deixa o server aberto
serv_socket.bind(addr)
serv_socket.listen(1)
print('wait connection' )
(con, cliente) = serv_socket.accept()
print( 'sucess' )
print( "wait request" )
response = con.recv(1024).decode('utf-8')
print( "request recepted: "+ response)
con.send('msg recept'.encode('utf'))
#encerra o server
serv_socket.close()