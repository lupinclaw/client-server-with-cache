# Rune Vannken 416 project client/cache/server project with tcp and snw implimentations
# i have not done much python before this project, so i refered to these offical documentions when 
# i had question about python stuff I was unfamilier with:
# https://docs.python.org/3/library/sys.html?highlight=sys%20argv#sys.argv
# https://docs.python.org/3/library/socket.html?highlight=socket#module-socket
# https://docs.python.org/3/library/os.path.html?highlight=os%20path#module-os.path

#cache; gets command line args and call an entry point based on protocol similer to server and client

import sys
import tcp_transport
import snw_transport

def main():
    args = sys.argv
    port_to_run = int(args[1])
    serverIP = args[2]
    server_port = int(args[3])
    protocol = args[4]

    if(protocol == "tcp"):
        tcp_transport.start_tcp_cache(port_to_run, serverIP, server_port)
    elif(protocol == "snw"):
        snw_transport.start_snw_cache(port_to_run, serverIP, server_port)
    

if __name__ == "__main__":
    main()