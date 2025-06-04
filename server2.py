#import required modules 
import os
import time
import socket
import threading

# Constants
HOST = '127.0.0.1'#local host
PORT = 1234 #port number to listen on
LISTENER_LIMIT = 5 #max number of client that can connect 
active_clients = [] #list to store active clients 

def send_file_to_all(sender_username,filename,filedata): # fuction to send file to all active clients 
    for user in active_clients: #for loop to iterate through all active clients
        try:
             header= f"{sender_username}~FILE:{filename}~{len(filedata)}"
             user[1].sendall(header.encode()) #send ecoded header to client used when sending file 
             time.sleep(0.1)  #a little delay to ensure header is sent before file data
             user[1].sendall(filedata) #send file data to client 
        except:
            remove_client(user[1]) # incase of error remove client from active list

                                

        


        
            

def listen_for_messages(client, username): #function to listen for message from client 
    while True: # loop to keep listening for messages

        try:
            message = client.recv(2048).decode('utf-8') # 2048 limits the size of message to be received
            if message.startswith("/sendfile "): # check if message starts with /sendfile to inndicate file transfer
                filepath = message.split(" ", 1)[1] # file path from message 
                if os.path.exists(filepath): # check if file exist
                    with open(filepath, "rb") as f: # opens file in binary mode especially for non-text files like pictures or videos 
                        filedata = f.read() # read file data
                    filename = os.path.basename(filepath) # get the  file name from the file path
                    send_file_to_all(username, filename, filedata) # send file to all active clients 
                else:
                    client.sendall(f"server~File '{filepath}' is no where to be found.".encode()) # if file does not exist or no where to be found send message to clinet 


            else:            
               if message.strip() == "": # checks if message is empty 
                    print(f"message from client {username} is empty. Disconnecting...") # if messge is empty print message and disconnect client
                    remove_client(client) # remove client from active list 
                    break # break the loop 
               
               else:
                    final_msg= username + "~" + message # join username and maessage with this symbol ~
                    send_messages_to_all(final_msg) # send message to all active  clients 
        except Exception as e: # catch any exception that occurs while receiving message
            print(f"Error receiving message from {username}: {e}")
            remove_client(client)
            break
     
# function to send message to specfic client 
def send_message_to_client(client, message):
    try:
        client.sendall(message.encode()) # covert message to bytes and send to client 
    except:
        remove_client(client)
# function to send message to all active client 
def send_messages_to_all(message): 
    for user in active_clients: # loop  through all active clients
        send_message_to_client(user[1], message) # send message to each client

def remove_client(client): # function to remove client from active client 
    for user in active_clients:
        if user[1] == client: # check if client is in active client list
            active_clients.remove(user) 
            break

def client_handler(client): # function to handle client connection
    try:
        username = client.recv(2048).decode('utf-8')
        if username:
            active_clients.append((username, client)) # add new client to active clients list 
            prompt_message = "Server~Welcome to the chat server, " + f"{username} has joined the chat." # welcome messge for new client

            send_messages_to_all(prompt_message) # send welcome message to all active clients 
            threading.Thread(target=listen_for_messages, args=(client, username), daemon=True).start() # thread to listen for messgaes from client 
        else:
            print("Empty username received. Closing connection.") # if username is emoty print message empty username received and close connection
            client.close() # close client conection 
    except:
        print("Error receiving username.")
        client.close()

def main(): # main function to start the server 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp socket for server because we are using tcp protocol and ipv4 
    server.bind((HOST, PORT)) # bind the server to the host and port 
    server.listen(LISTENER_LIMIT) # listens to incoming connection with the limit of 5 set
    print(f"Server running on {HOST}:{PORT} and listening...") # print message to indicate the server is running and listening 

    while True: # loop to keep the server runing and  accpts new connection
        try:
            client, address = server.accept()
            print(f"New connection from {address}")
            threading.Thread(target=client_handler, args=(client,), daemon=True).start() # handle the new client connection in a seprate thread 
        except Exception as e:
            print(f"Error accepting new connection: {e}")

if __name__ == "__main__":
    main()
