# Rune Vannken 416 project client/cache/server project with tcp and snw implimentations
# i have not done much python before this project, so i refered to these offical documentions when 
# i had question about python stuff I was unfamilier with:
# https://docs.python.org/3/library/sys.html?highlight=sys%20argv#sys.argv
# https://docs.python.org/3/library/socket.html?highlight=socket#module-socket
# https://docs.python.org/3/library/os.path.html?highlight=os%20path#module-os.path    

#client; loops taking commands until quit command, calls entry point in the xxx_transport.py based of protocol+command
import sys
import tcp_transport
import snw_transport
import os
import time

CLIENT_FILES = "client_files"

def main():
    args = sys.argv
    serverIP = args[1]
    server_port = int(args[2])
    cacheIP = args[3]
    cache_port = int(args[4])
    protocol = args[5]

    while True:
        command_path = input("Enter command: ")
        command_path = command_path.split()
        
        if(command_path[0] == "quit"):
            print("Exiting program!")
            sys.exit()

        filepath = command_path[1]
        if(protocol == "tcp"):
            if(command_path[0] == "put"):
                print("Awaiting server response.")
                file = tcp_transport.put(filepath, serverIP, server_port)
            elif(command_path[0] == "get"):
                file = tcp_transport.get_cache(filepath, cacheIP, cache_port)
                with open(os.path.join(CLIENT_FILES, filepath), "w", encoding = "utf-8") as output:
                    output.write(file)

        elif(protocol == "snw"):
            if(command_path[0] == "put"):
                print("Awaiting server response.")
                file = snw_transport.put(filepath, serverIP, server_port)
            elif(command_path[0] == "get"):
                file = snw_transport.get_cache(filepath, cacheIP, cache_port)
        #pause befoer each command fix an issue i have having with client stepping on top of cache and server on my local network
        time.sleep(0.5)

        

if __name__ == "__main__":
    main()