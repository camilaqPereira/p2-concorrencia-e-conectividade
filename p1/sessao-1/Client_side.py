import socket


ip = '127.0.0.1'
port = 5000
addr = ((ip,port))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(addr)

mensagem = input('digite sua mensagem: ')
client_socket.send(mensagem.encode('utf-8'))
print ('mensagem enviada' )
print('aguardando resposta')
response = client_socket.recv(1024).decode('utf-8')
print('server response: ' + response)
client_socket.close()