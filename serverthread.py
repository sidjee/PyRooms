#THIS PROGRAM IS USED TO CREATE MULTI-CHAT-ROOM SERVER
#WHICH CAN ACCEPT COONECTIONS FROM CLIENTS AND CREATE MULTIPLE 
# PASSWORD PROTECTED ROOMS WHICH INDEPENDENTLY SERVE AS GROUP CHAT

###################THIS PROGRAM USES MULTITHREADING##################

# NOTE:- THIS PROGRAM IS TO BE USED FOR COMMAND LINE CLIENTS LIKE 
# NETCAT , TELNET , etc


import socket
import sys
import select
import threading
import Queue
import time

if len(sys.argv) != 2:
	print("Usage: python server.py [ port-number ]")
	sys.exit()

server_sock = socket.socket()
host = '0.0.0.0'
port = int(sys.argv[1])
server_sock.bind((host,port));


print('Listener on port'+str(port))
print('Waiting for connections')

wlcm_msg = '***********Welcome to chat service***********\n'

q = Queue.Queue(100)
server_sock.listen(4)

rooms={}					#{Room Name: Password}
client_sockets = {}			#{Client Socket:[Client Name, Room Name]}
room_client = {}			#{Room Name: Client Name}

lock = threading.Lock()

def client_thread(new_sock,new_addr):
	global rooms
	global client_sockets
	global room_client
	global q
	print('New connection accepted from '+str(new_addr))
		
	new_sock.send(wlcm_msg)
	new_sock.send("Pl enter your name and room in (name,room) format\n")

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

		if y[0] not in room_client.keys():
			
			room_client[room_name] = [cl_name]
			##########################################################
			lock.release()

			new_sock.send('Write the password for new room\n')
			password = new_sock.recv(1024)
			if password == '':
				new_sock.close
				del room_client[room_name]

			else:
				lock.acquire()
				##########################################################
				
				new_sock.send("New room is opened\n")
				rooms.update({room_name:password})
				new_dick = {new_sock:[cl_name,room_name]}
				client_sockets.update(new_dick)
				###############################################################
				lock.release()

		else :
			##############################################################
			lock.release()
			while True:
				new_sock.send('Write the password for existing room\n')
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
				if i==40:
					break
				
				if room_name in rooms.keys():	
					if password == rooms[room_name]:
					
						lock.acquire()
					####################################################################
						room_client[room_name].append(cl_name)
						new_sock.send('Added you to the room. Now you can send/recv messages..\n')

						new_dick = {new_sock:[cl_name,room_name]}
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
				room = client_sockets[client][1]

				if data == '':
					print ('Client disconnected ip = '+str(client.getpeername()))
					client.close
					
					room_client[room].remove(client_sockets[client][0])
					if room_client[room] == []:
						del room_client[room]
						del rooms[room]
						
					del client_sockets[client]

				else:
					for client1 in client_sockets.keys():
						if client_sockets[client1][1] == room:

							if  client1 != client:
								client1.send(str(client_sockets[client][0]+' : '+data))


class Mythread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		self.msg_thread = threading.Thread( target = msg_transfer)
		self.msg_thread.start()

		while True:
			
			new_sock, new_addr = server_sock.accept()
			self.cl_thread = threading.Thread( target = client_thread, args = (new_sock,new_addr,))
			self.cl_thread.start()

				
thread = Mythread()

thread.start()

