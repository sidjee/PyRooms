import socket
import sys
#import ast
import select
import threading
import Queue
import time

if len(sys.argv) != 2:
	print("Usage: python server.py [ port-number ]")
	sys.exit()

server_sock = socket.socket()
host = '127.0.0.1'
port = int(sys.argv[1])
server_sock.bind((host,port));


print('Listener on port'+str(port))
print('Waiting for connections')

wlcm_msg = '***********Welcome to chat service***********\n'

#max_clients = 30
q = Queue.Queue(100)
server_sock.listen(4)

rooms={}
client_sockets = {}
room_client = {}

lock = threading.Lock()

def client_thread(new_sock,new_addr):
	#new_sock,new_addr = server_sock.accept()
	global rooms
	global client_sockets
	global room_client
	global q
	print('New connection accepted from '+str(new_addr))
		
	new_sock.send(wlcm_msg)
	#new_sock.send("Pl enter your name and room in (name,room) format\n")

	while True:
		while True:
			msg = new_sock.recv(1024)
			if msg == '':
				new_sock.close
				break
			if(',' in msg ):
				break
			else:
				new_sock.send("Invalid message\n")
		if msg == '':
			break
		lock.acquire()
		##############################################
		
		room_name = msg.split(',')[1]
		cl_name = msg.split(',')[0]
		if room_name in room_client.keys():
			if cl_name not in room_client[room_name]:
				break
			else:
				new_sock.send('Name exists!! Pl enter again.\n')
				#########################################################
				lock.release()
		else:
			break

	if msg != '':
		q.put([room_name,new_sock])

		y = None
		s= q.qsize()
		z = Queue.Queue(100)
		for i in range(s):
			x=q.get()
			if new_sock == x[1]:
				y = x
			else:
				z.put(x)
		
		q = z
		#lock.release()
		if y[0] not in room_client.keys():
			
			room_client[room_name] = [cl_name]
			##########################################################
			lock.release()

			new_sock.send('req-pass1\n')
			password = new_sock.recv(1024)
			if password == '':
				new_sock.close
				del room_client[room_name]

			else:
				lock.acquire()
				##########################################################
				#room_client[room_name] = [cl_name]
				#new_sock.send("New room is opened\n")
				rooms.update({room_name:password})
				new_dick = {new_sock:cl_name}
				client_sockets.update(new_dick)
				###############################################################
				lock.release()

		else :
			##############################################################
			lock.release()
			while True:
				new_sock.send('req-pass0')
				password = new_sock.recv(1024)
				i=0
				while True:
					i+=1
					if room_name in rooms.keys():
						break
					if i == 40:
						new_sock.send('Invalid room..Exit this window!')
						new_sock.close
						break
					time.sleep(.5)
				
				if room_name in rooms.keys():	
					if password == rooms[room_name]:
					
						lock.acquire()
					####################################################################
						room_client[room_name].append(cl_name)
						#new_sock.send('Added you to the room. Now you can send/recv messages..\n')

						new_dick = {new_sock:cl_name}
						client_sockets.update(new_dick)
						###########################################################################
						lock.release()
					
						break
					
					new_sock.send('Wrong password :(( Try again\n')
				
def msg_transfer():

	global rooms
	global client_sockets
	global room_client

	while True:
		
		ins = []
		ins = list(client_sockets.keys())
		#print(ins)
		i = None
		i,o,e = select.select(ins,[],[],0.5)
		#print(ins)
		if i!=[]: 
			for client in i :
					
				data = client.recv(1024)
					
				if data == '':
					print ('Client disconnected ip = '+str(client.getpeername()))
					client.close
					
					for room in room_client.keys():
						if client_sockets[client] in room_client[room]:
							room_client[room].remove(client_sockets[client])
							break
					del client_sockets[client]

				else:
					for room in room_client.keys():
						if client_sockets[client] in room_client[room]:

							for clname in room_client[room]:
								if clname != client_sockets[client]:
									for key,name in client_sockets.items():
										if name == clname:
											key.send(str(client_sockets[client]+' : '+data))
							break



class Mythread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		#global msg_transfer
		self.msg_thread = threading.Thread( target = msg_transfer)
		self.msg_thread.start()

		while True:
			
			new_sock, new_addr = server_sock.accept()
			self.cl_thread = threading.Thread( target = client_thread, args = (new_sock,new_addr,))
			self.cl_thread.start()

				
thread = Mythread()

thread.start()

