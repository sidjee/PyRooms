
########## NOT FOR RUNNING ############

import threading

lock = threading.Lock()

def client_thread():
	#new_sock,new_addr = server_sock.accept()
	print('New connection accepted from '+str(new_addr))
		
	new_sock.send(wlcm_msg)

	msg = new_sock.recv(1024)
	room_name = msg.split(',')[1]
	cl_name = msg.split(',')[0]
		
	if room_name not in rooms.keys():
		new_sock.send('req-pass1')
		password = new_sock.recv(1024)
		
		lock.acquire()
		room_client[room_name] = [cl_name]
		rooms.update({room_name:password})
		new_dick = {new_sock:cl_name}
		client_sockets.update(new_dick)
		lock.release()

	else :
		while True:
			new_sock.send('req-pass0')
			password = new_sock.recv(1024)
				if password == rooms[room_name]:
				
				lock.acquire()
				room_client[room_name].append(cl_name)
				print('Added you to list of clients')
				new_dick = {new_sock:cl_name}
				client_sockets.update(new_dick)
				lock.release()

				break
			
			new_sock.send('wrong-pass')
