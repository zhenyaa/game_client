import socket
import threading
from time import sleep

import struct
import uuid
import select
import game_flow

def command_selector(command, command_args, conn):
    print(command_args)
    match command:
        case "clients":
            clr = game_flow.ClientsList(cmd="ACK")
            game_flow.send_message(conn, 1, clr) 
        case "add_client":
            room = game_flow.RoomData(joined_uuid=command_args[0])
            game_flow.send_message(conn, 2, room) 
        case "leave":
            conn.shutdown(socket.SHUT_WR)
            conn.close()

def listen_for_messages(conn):
    try:
        while True:
            # Receive the header first
            data = conn.recv(8)  # Size of the header (msg_type and msg_size)
            if data:
                print(data)
                msg_type, msg_size = struct.unpack("Ii", data)
                print(f"Message type: {msg_type}, Message size: {msg_size}")
                
                # Handle different message types
                if msg_type == 0:
                    print("case Greeting")
                    d = game_flow.Greeting.deserialize(conn.recv(msg_size))
                    print(d)
                    d.uuid = game_flow.CLIENT_STR.encode()
                    print(d)
                    game_flow.send_message(conn, 0, d)
                if msg_type == 1:
                    print("case UserList")
                    ul = game_flow.ClientsList.deserialize(conn.recv(msg_size))
                    print(ul)
                if msg_type == 2:
                    print("case add client")
                    ul = game_flow.RoomData.deserialize(conn.recv(msg_size))
                    print(ul)
                # else:
                #     print("Connection closed or no data received.")
                #     break
    except Exception as e:
        print(f"Error while receiving messages: {e}")
    finally:
        conn.close()

def handle_user_input(conn):
    import shlex
    while True:
        cmd = input("Enter command: ")
        if cmd:
            args = shlex.split(cmd)  # Разбиваем команду на аргументы
            command_name = args[0]  # Первое слово — это команда
            command_args = args[1:]  # Остальные слова — аргументы

            command_selector(command_name, command_args, conn)  


def main():
    conn = socket.create_connection(("127.0.0.1", 12345))
    
    message_thread = threading.Thread(target=listen_for_messages, args=(conn,))
    input_thread = threading.Thread(target=handle_user_input, args=(conn,))

    # Start the threads
    message_thread.start()
    input_thread.start()

    # Wait for the threads to finish
    message_thread.join()
    input_thread.join()


if __name__ == "__main__":
    main()