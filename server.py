#This server file is used to create chat rooms but 
#performance is compromised as this program uses select 
#for selecting clients.

################THIS IS A SINGLE THREAD PROGRAM################


import socket
import sys
import ast
import select
import threading

if len(sys.argv) != 2:
	print("Usage: python server.py [ port-number ]")
	sys.exit()

server_sock = socket.socket()
host = '127.0.0.1'
port = int(sys.argv[1])
server_sock.bind((host,port));


print('Listener on port'+str(port))
print('Waiting for connections')

wlcm_msg = 'Welcome to chat service'

#max_clients = 30

server_sock.listen(4)

rooms={}
client_sockets = {}
room_client = {}
while True:
	ins = [server_sock]
	outs = []
	for cl in client_sockets.keys():
		ins.append(cl)

	print('again')
	i,o,e = select.select(ins,outs,[])

	if server_sock in i:
		new_sock, new_addr = server_sock.accept()
		print('New connection accepted from '+str(new_addr))
		
		new_sock.send(wlcm_msg)

		msg = new_sock.recv(1024)
		room_name = msg.split(',')[1]
		cl_name = msg.split(',')[0]

		
		if room_name not in rooms.keys():
			new_sock.send('req-pass1')
			password = new_sock.recv(1024)
			room_client[room_name] = [cl_name]
			rooms.update({room_name:password})
			new_dick = {new_sock:cl_name}
			client_sockets.update(new_dick)


		else :
			while True:
				new_sock.send('req-pass0')
				password = new_sock.recv(1024)

				if password == rooms[room_name]:
					room_client[room_name].append(cl_name)
					print('Added you to list of clients')
					
					new_dick = {new_sock:cl_name}
					client_sockets.update(new_dick)
					break
				
				new_sock.send('wrong-pass')

	for client in client_sockets :
		
		if client in i:
			data = client.recv(1024)
			
			if data == '':
				print ('Client disconnected ip = '+str(client.getpeername()))
				client.close
				del client_sockets[client]
				for room in room_client.keys():
					room_client[room].remove(client_sockets[client])

			else:
	 			for room in room_client.keys():
	 				if client_sockets[client] in room_client[room]:

						for clname in room_client[room]:
							if clname != client_sockets[client]:
								for key,name in client_sockets.items():
									if name == clname:
										key.send(str(client_sockets[client]+' : '+data))

