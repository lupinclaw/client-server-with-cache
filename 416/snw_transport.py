# Rune Vannken 416 project client/cache/server project with tcp and snw implimentations
# i have not done much python before this project, so i refered to these offical documentions when 
# i had question about python stuff I was unfamilier with:
# https://docs.python.org/3/library/sys.html?highlight=sys%20argv#sys.argv
# https://docs.python.org/3/library/socket.html?highlight=socket#module-socket
# https://docs.python.org/3/library/os.path.html?highlight=os%20path#module-os.path

#snw implimentation, uses tcp for commands and udp for data 

import os
import socket

#size from assigment doc
MESSAGE_SIZE = 1000
LOCAL_HOST = "localhost" #also from doc, server doesnt get an IP to bind on in the doc, it only gets protocol 
                         #and port form command line so i used this cuz it made sense from the examples 

#creates snw server, gets command over tcp and then opens UDP sends or reveives based on command, and sends proper responce 
def start_snw_server(port):
    #gets the commands over tcp as per doc, but after we check the command and get the file name, we close the tcp socket and open a udp one for file transfer
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LOCAL_HOST, port))
    server_socket.listen()

    while True:
        client, address = server_socket.accept()
        command = client.recv(MESSAGE_SIZE).decode("utf-8")
        command = command.split()
        filename = command[1]
        filepath = os.path.join("server_files", filename)
        
        if(command[0] == "get"):
            client.close() #no more tcp as we have recieved the commands
            with open(filepath, "r", encoding="utf-8") as output:
                    data = output.read()
            sender(address, data)
        elif(command[0] == "put"):
            client.send("File successfully uploaded.".encode("utf-8"))
            client.close()
            reciever(address, filepath)
                  
# gets command and file name form tcp message
# checks if the chache has the file locally, if so its sends "File delivered from cache." and then closes the tcp connection
# and then sends the file over UDP using the sender() method
# if it doesnt have the file it calls get_server() and sends "File delivered from origin." and then closes the tcp connection
def start_snw_cache(port, serverIP, server_port):
    #listens on tcp 
    cache_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cache_socket.bind((LOCAL_HOST, port))
    cache_socket.listen()

    while True:
        client, address = cache_socket.accept()
        filename = client.recv(MESSAGE_SIZE).decode("utf-8")
        cache_file_path = os.path.join("cache_files", filename)

        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r", encoding="utf-8") as output:
                data = output.read()
            client.send("File delivered from cache.".encode("utf-8"))
            client.close()#close tcp to use udp
            sender(address, data)
        else:
            get_server(filename, serverIP, server_port)
            with open(cache_file_path, "r", encoding="utf-8") as output:
                data = output.read()
            client.send("File delivered from origin.".encode("utf-8"))
            client.close()#close tcp to use udp
            sender(address, data)
                
            
#recieves the tcp message form start_snw_cache then closes the tcp connection
#if its a local cache file it sends the file to the client using the sender() method
#if its a server file we first use receiver() method to get the file and store it in the cache for future use
# then we the reviever method with the client_files path, and then use sender() method to send the file from cache to the client 
#called by client
def get_cache(file, cacheIP, cachePORT):
    #tcp to send file name to the cache
    client_get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_get_socket.connect((cacheIP, cachePORT))
    client_get_socket.send(f"{file}".encode("utf-8"))
    address = client_get_socket.getsockname()
    client_file_path = os.path.join("client_files", file)

    responce = client_get_socket.recv(MESSAGE_SIZE).decode("utf-8")
    client_get_socket.close()
    if responce == "File delivered from cache.":
        reciever(address, client_file_path)
        print(f"Server response: {responce}")
    elif responce == "File delivered from origin.":
        reciever(address, client_file_path)
        print(f"Server response: {responce}")


#called by cache if it does not have the file, sends get to server, and call receiver side UDP for the cache 
def get_server(file, serverIP, serverPORT):
    #sends a get request to the server over tcp
    cache_get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cache_get_socket.connect((serverIP, serverPORT))
    cache_get_socket.send(f"get {file}".encode("utf-8"))
    address = cache_get_socket.getsockname()
    cache_get_socket.close()
    cache_file_path = os.path.join("cache_files", file)
    reciever(address, cache_file_path)

#client side put command, sends put command over tcp to server, and then calls the sender side of UDP with the file
def put(file, serverIP, serverPORT):
    file_path = os.path.join("client_files", file)
    server_put_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_put_socket.connect((serverIP, serverPORT))
    server_put_socket.send(f"put {file}".encode("utf-8"))
    address = server_put_socket.getsockname()
    responnce = server_put_socket.recv(MESSAGE_SIZE).decode("utf-8")
    server_put_socket.close()
    with open(file_path, "r", encoding="utf-8") as output:
                    data = output.read()
    sender(address,data)
    print(f"Server response: {responnce}")

#acts as the receiver side of UDP, recieves data from specficed address and writes it specifed param filepath to impliemtnts time outs and sends ack and fin
def reciever(adress_tuple, filepath):
    #print("recieving") #debuggin
    #print(adress_tuple) #debuggin
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind(adress_tuple)
    msg, address = receiver_socket.recvfrom(MESSAGE_SIZE)
    msg = msg.decode("utf-8")
    msg = msg.split(":")
    legnth = int(msg[1])

    if(msg[0] == "LEN"):
        data = ""
        received_so_far = 0
        while received_so_far < legnth:                
            receiver_socket.settimeout(1)#timeout according to doc specification
            try:
                chunk, address = receiver_socket.recvfrom(MESSAGE_SIZE)
                chunk = chunk.decode("utf-8")
                data += chunk
                received_so_far += len(chunk)
                #print(f"progress: {received_so_far}/{legnth}") #debugging
                #ack
                receiver_socket.sendto("ACK".encode("utf-8"), address)
            except socket.timeout:
                print("Did not receive data. Terminating.") #as per doc
                receiver_socket.close()
                return
        #fin
        receiver_socket.sendto("FIN".encode("utf-8"), address)
        with open(filepath, "w", encoding="utf-8") as output:
            output.write(data)
    receiver_socket.close()

#acts as the sender side of UDP, sends param data to specficed address impliemtnts time outs for ack and fin
def sender(adress_tuple, data):
    #print("sending") #debuggin
    #print(adress_tuple) #debuggin
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg_chunks = []
    for i in range(0, len(data), MESSAGE_SIZE):
        chunk = data[i:i + MESSAGE_SIZE]
        msg_chunks.append(chunk)

    len_msg = f"LEN:{len(data)}"
 
    sender_socket.sendto(len_msg.encode("utf-8"),adress_tuple)

    for tmp in msg_chunks:
        sender_socket.sendto(tmp.encode("utf-8"),adress_tuple)
        sender_socket.settimeout(1)
        try:
            ack, _ = sender_socket.recvfrom(3)
            if ack.decode("utf-8") == "ACK":
                continue
        except socket.timeout:
            print("Did not receive ACK. Terminating.")
            sender_socket.close()
    try:
        fin, _ = sender_socket.recvfrom(3)
        if fin.decode("utf-8") == "FIN":
            sender_socket.close()
            return
    except socket.timeout:
        print("Did not receive FIN. Terminating.")
        sender_socket.close()


