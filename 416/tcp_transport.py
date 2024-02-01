# Rune Vannken 416 project client/cache/server project with tcp and snw implimentations
# i have not done much python before this project, so i refered to these offical documentions when 
# i had question about python stuff I was unfamilier with:
# https://docs.python.org/3/library/sys.html?highlight=sys%20argv#sys.argv
# https://docs.python.org/3/library/socket.html?highlight=socket#module-socket
# https://docs.python.org/3/library/os.path.html?highlight=os%20path#module-os.path

#tcp implimentation, uses tcp sockets for commands and data

import os
import socket

#size from assigment doc
MESSAGE_SIZE = 1000
LOCAL_HOST = "localhost" #also from doc, server doesnt get an IP to bind on in the doc, it only gets protocol 
                         #and port form command line so i used this cuz it made sense from the examples 

#creates a tcp server which listens for commands ove tcp and then returns to file if get, or saves the files if put, and retursn approperiate responce
def start_tcp_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LOCAL_HOST, port))
    server_socket.listen()
    while True:
        client, _ = server_socket.accept()
        command = client.recv(MESSAGE_SIZE).decode("utf-8")
        command = command.split()
        filename = command[1]
        filepath = os.path.join("server_files", filename)
        if(command[0] == "get"):
            if(os.path.exists(filepath)):
                with open(filepath, "r", encoding = "utf-8") as output:
                    data = output.read()
                    client.send(data.encode("utf-8"))
        elif(command[0] == "put"):
            fileData = ""
            while True:
                msg = client.recv(MESSAGE_SIZE).decode("utf-8")
                if(len(msg) < MESSAGE_SIZE):
                    fileData += msg
                    break
                fileData += msg
            with open(filepath, "w", encoding = "utf-8") as output:
                output.write(fileData)
            client.send("File successfully uploaded.".encode("utf-8"))
        client.close()

#creates the cache which listens for get from client, checks if it has the files, sends it back if so, else calls server_get to get files from server
#saves that server files locally and sends back a copy of the file along with appropriate server msg for where the file came from
def start_tcp_cache(port, serverIP, serverPORT):
    cache_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cache_socket.bind((LOCAL_HOST, port))
    cache_socket.listen()
    while True:
        client, _ = cache_socket.accept()
        filename = client.recv(MESSAGE_SIZE).decode("utf-8")
        filepath = os.path.join("cache_files", filename)

        if(os.path.exists(filepath)):
            with open(filepath, "r", encoding = "utf-8") as output:
                data = output.read()
                client.send(data.encode("utf-8"))
                client.send("splitonme File delivered from cache.".encode("utf-8"))
        else:
            fromServerFile = get_server(filename, serverIP, serverPORT)
            with open(filepath, "w", encoding = "utf-8") as output:
                output.write(fromServerFile)
                client.send(fromServerFile.encode("utf-8"))
                client.send("splitonme File delivered from origin.".encode("utf-8"))
        client.close()



#called by client, sends get command to cache and gets the returns responce and prints it
def get_cache(filepath, cacheIP, cachePORT):
    client_get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_get_socket.connect((cacheIP, cachePORT))
    client_get_socket.send(f"{filepath}".encode("utf-8"))

    returnedData = ""
    while True:
        msg = client_get_socket.recv(MESSAGE_SIZE).decode("utf-8")
        if(len(msg) < MESSAGE_SIZE):
            returnedData += msg
            break
        returnedData += msg
    data, response = returnedData.split("splitonme", 1)
    print(f"Server response:{response}")
    client_get_socket.close()
    return data

#called by cache if it does not have the file
def get_server(filepath, serverIP, serverPORT):
    cache_get_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cache_get_socket.connect((serverIP, serverPORT))
    cache_get_socket.send(f"get {filepath}".encode("utf-8"))

    fileData = ""
    while True:
        msg = cache_get_socket.recv(MESSAGE_SIZE).decode("utf-8")
        if(len(msg) < MESSAGE_SIZE):
            fileData += msg
            break
        fileData += msg

    cache_get_socket.close()
    return fileData

#gets message from client_files and sends it to server, receivers server responce and prints it
def put(filename, serverIP, serverPORT):
    server_put_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_put_socket.connect((serverIP, serverPORT))
    server_put_socket.send(f"put {filename}".encode("utf-8"))
    filepath = os.path.join("client_files", filename)
    
    if(os.path.exists(filepath)):
        with open(filepath, "r", encoding = "utf-8") as output:
            data = output.read()
            server_put_socket.send(data.encode("utf-8"))
        response = server_put_socket.recv(MESSAGE_SIZE).decode("utf-8")
        print(f"Server response: {response}")
    server_put_socket.close()


