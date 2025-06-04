#Iimport required modules 
import socket 
import threading
#constants
HOST = '127.0.0.1'#local host 
PORT = 1234 # port number connect s to the server 



def listen_for_messages_from_server(client): # function to listen for messages from server
    while True: # loop to keeep listening for messages 
        try:
            message = client.recv(2048).decode('utf-8') # 2048 shos limit of message to be recived 
            if message: # checks if messgae is empty
                if "FILE:" in message: # checks if message contains FILE to inidcate file transfer 
                    username,file_header,filesize = message.split("~") # splits message into username, file hedaer and file size 
                    filename = file_header.split(":")
                    filesize = int(filesize)
                    print(f"[{username}] is sending a file: {filename[1]} of size {filesize} bytes.") # prints message to indicate file transfer 

                    filedata= b"" # variable to store file data 
                    while len(filedata) < filesize:
                        chunk= client .recv(min(2048,filesize - len(filedata))) # gets file data in chunks of 2048 bytes 
                        if not chunk:
                            break
                        filedata += chunk # accumlates file data 
                    if filedata:    

                        with open(f"received_{filename[1]}", "wb") as f: #stores file data in binary 
                             f.write(filedata) # file data is directed to file 
                    print(f"File '{filename}' received and saved as 'received_{filename[1]}'.") # prints message to indicate file has been recieved and saved as recived _file 
                else: # if message does not coontain FILE then it is nirmal message 

                   username, content = message.split("~")
                print(f"[{username}] {content}")
            else:
                print("Empty message received.") # prints if message is empty 
        except Exception as e:
            print(f"Connection to server lost Error: {e}") # prints if here coonection to server is lost 
            client.close() # close client connection  
            break

def send_message_to_server(client): # function to sned message to server 
    while True:
        message = input("Message: ") # takes input from user 
        if message:
            client.sendall(message.encode()) # encodes message from strig to bytes to sned message to the server 
        else:
            print("Empty message. Disconnecting.") # prints if message is empty and disconnects client
            client.close() # closes client connection to the server 
            break

def communicate_to_server(client): # function to communicate to the server
    username = input("Enter username: ") # takes input from user for username 
    if username:
        client.sendall(username.encode()) # converts username string to bytes and send it server 
    else:
        print("Username cannot be empty.") # prints if username is empty 
        client.close() # closes client connection to the server 
        exit(0) # exits the program

def main(): # main function to run the client.py 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create ssocket object with ipv4 and tcp protocol 
    try:
        client.connect((HOST, PORT)) # connects to server using host and port 
        print("Connected to server.") # prints message to sho a connection to the server has been made 
        communicate_to_server(client) # communicates to the server to send username 
        threading.Thread(target=listen_for_messages_from_server, args=(client,), daemon=True).start() # thread to listen for messages from server 
        send_message_to_server(client) # recalls function to send message to server 
    except Exception as e: # catches any error that occurs while connecting to the server 
        print(f"Error: {e}")
        client.close()

if __name__ == "__main__": #chekcs if this program is being run on the main 
    main()  