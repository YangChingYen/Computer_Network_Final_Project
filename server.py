import socket
import os
import threading
import json
import csv
import pymysql
from datetime import datetime

PORT = 7831
HTML_HOME_PATH = "home_page.html"
HTML_SCPT_PATH = "script.js"
CSS_PATH       = "styles.css"
DATA_BASE_PATH = "login_info.csv"
AUDIO_DIR_PATH = "audio_info.csv"
VIDEO_DIR_PATH = "video_info.csv"
count_id = 0
lock = threading.Lock()
command = ""

def receive_data(client_socket, remain_len):
    data = b''
    while remain_len > 0:
        chunk = client_socket.recv(min(4096,remain_len))
        if not chunk:
            break
        data += chunk
        remain_len -= len(chunk)
        print(f"remain_len:{remain_len}")
    print("end==")
    return data

def parse_multipart(data, boundary):
    parts = data.split(boundary)
    
    # Process each part
    for part in parts:
        if b'Content-Disposition: form-data' in part:
            # Extract filename and content
            filename_start = part.find(b'filename="') + len(b'filename="')
            filename_end = part.find(b'"', filename_start)
            filename = part[filename_start:filename_end].decode('utf-8')

            content_start = part.find(b'\r\n\r\n') + len(b'\r\n\r\n')
            content = part[content_start:]

            # Process the file content, e.g., save it to disk
            with open(filename, 'wb') as f:
                f.write(content)

db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "12345678",
    "db": "message_board",
    "charset": "utf8"
}

try:
    conn = pymysql.connect(**db_settings)
    cursor = conn.cursor()
        # command = "INSERT INTO message(id,Name,Message,Type,Date)VALUES(%s,%s, %s, %s, %s)"
        # cursor.execute(command, ("test_name", "hello test", "1", "4:43"))
        # cursor.execute(command, (int(1),"test_name", "hello test2", "1", "4:44"))
        
        # command = "DELETE FROM message where id = %s"
        # cursor.execute(command,(int(0)))
        # cursor.execute(command,(int(1)))
except Exception as ex:
    print(ex)
    
def all_message():
    global count_id
    try:
        with lock:
            command = "SELECT * FROM message"
            cursor.execute(command)
            result = cursor.fetchall()
            data_len = len(result)
            if data_len!=0:
                count_id = result[data_len-1][0] + 1
            else:
                count_id = 0
            print(f"current data:\n{result}\n=================\n")
            print(f"count start at {count_id}")
            result = [i for i in result]
            return result
    except Exception as ex:
        print(ex)
        return

all_message()
    
def insert_message(message):
    all_message()
    global count_id
    try:
        with lock:
            command = "INSERT INTO message(id,Message,Type,Date)VALUES(%s, %s, %s, %s)"
            cursor.execute(command, (int(count_id), message['message'], message['type'], message['date']))
            count_id += 1
            conn.commit()
            return True
    except Exception as ex:
        print(ex)
        return False

def check_login_credentials(account, password):
    # Read the CSV file and check for valid login credentials
    with open(DATA_BASE_PATH, 'r', newline='\n') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['account'] == account: 
                if row['password'] == password:
                    return True
                else:
                    return False
    return False

def reg_check_exist(account, password):
    exist = False
    with open(DATA_BASE_PATH, 'r', newline='\n') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['account'] == account: 
                exist = True
    if not exist:
        with open(DATA_BASE_PATH, 'a', newline='\n') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([account, password])
            print("done register!")
        return False
    else:
        return True
    
def store_audio(audio_content):
    store_id = 0
    current_datetime = datetime.now()
    audio_content = audio_content.split(b"\r\n\r\n", 1)[1]
    print(audio_content)
    formatted_datetime = current_datetime.strftime("%m/%d %I:%M %p")
    with open(AUDIO_DIR_PATH, 'r', newline='\n') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        is_used = [int(row['id']) for row in csv_reader]
        print(f"audio_id: {is_used}")
        while store_id in is_used:
            store_id += 1
    audio_path = f"./audio/{store_id}.mp3"    
    with open(audio_path, 'wb') as audio_file:
        audio_file.write(audio_content)
    with open(AUDIO_DIR_PATH, 'a', newline='\n') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([store_id])
    message = {
        "message": f"{store_id}",
        "type"   : "Audio",
        "date"   : f"{formatted_datetime}"           
    }
    return message

def store_video(video_content, boundary):
    store_id = 0
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%m/%d %I:%M %p")
    with open(VIDEO_DIR_PATH, 'r', newline='\n') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        is_used = [int(row['id']) for row in csv_reader]
        print(f"video_id: {is_used}")
        while store_id in is_used:
            store_id += 1
    video_path = f"./video/{store_id}.mp4"  
    
    parts = video_content.split(boundary)
    
    # Process each part
    for part in parts:
        if b'Content-Disposition: form-data' in part:
            # Extract filename and content

            content_start = part.find(b'\r\n\r\n') + len(b'\r\n\r\n')
            content = part[content_start:]

            # Process the file content, e.g., save it to disk
            with open(video_path, 'wb') as f:
                f.write(content)
    

    with open(VIDEO_DIR_PATH, 'a', newline='\n') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([store_id])
    message = {
        "message": f"{store_id}",
        "type"   : "Video",
        "date"   : f"{formatted_datetime}"           
    }
    return message
    
def handle_single_request(client_socket):
    buffer_size = 1024
    request = b""
    request = client_socket.recv(buffer_size)
    return request

def serve_client(client_socket):
    response = b""
    print("I'm a new client")
    request = b""
    while True:
        # Read the HTTP request
        request = handle_single_request(client_socket)
        print("================================================================>")
        # print(request)
        if not request:
            break
        req = request.split(b" ")
        if (req[0] == b'GET') :
            if (req[1] == b'/'):
                # Respond with the content of the HTML file
                try:
                    with open(os.path.join(os.getcwd(), HTML_HOME_PATH), "rb") as file:
                        content = file.read()
                        response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: text/html\r\n"
                            b"Content-Length: " + str(len(content)).encode("utf-8") + b"\r\n\r\n" + content
                        )
                except FileNotFoundError:
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found"
            elif (req[1] == b'/login.html'):
                # Respond with the content of the HTML file
                try:
                    with open(os.path.join(os.getcwd(), "login.html"), "rb") as file:
                        content = file.read()
                        response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: text/html\r\n"
                            b"Content-Length: " + str(len(content)).encode("utf-8") + b"\r\n\r\n" + content
                        )
                except FileNotFoundError:
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found"
            elif (req[1] == b'/script.js'):
                try:
                    with open(os.path.join(os.getcwd(), HTML_SCPT_PATH), "rb") as file:
                        content = file.read()
                        response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: application/javascript\r\n"
                            b"Content-Length: " + str(len(content)).encode("utf-8") + b"\r\n\r\n" + content
                        )
                except FileNotFoundError:
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found"
            elif (req[1] == b'/styles.css'):
                print("get css")
                try:
                    with open(os.path.join(os.getcwd(), CSS_PATH), "rb") as file:
                        content = file.read()
                        response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: text/css\r\n"
                            b"Content-Length: " + str(len(content)).encode("utf-8") + b"\r\n\r\n" + content
                        )
                except FileNotFoundError:
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found"
            elif (req[1] == b'/favicon.ico'):
                response = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: image/x-icon\r\n"
                    b"Content-Length: 0\r\n\r\n"
                )
                # print("responded")
            elif (req[1] == b'/message_board'):
                all_msg = all_message()
                all_msg_list = "\n".join(["$$$".join(map(str,i)) for i in all_msg])
                content = all_msg_list.encode("utf-8")
                print(f"================\ncontent->{content}\n")
                response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: application/javascript\r\n"
                            b"Content-Length: " + str(len(content)).encode("utf-8") + b"\r\n\r\n" + content
                        )
            elif (req[1].find(b'/getAudio') != -1):
                audio_req = req[1].split(b"id=")
                audio_id  = int(audio_req[1])
                print(f"audio_id={audio_id}")
                with open(f"./audio/{audio_id}.mp3", "rb") as audio_file:
                    audio_content = audio_file.read()
                    response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: audio/mp3\r\n"
                            b"Content-Length: " + str(len(audio_content)).encode("utf-8") + b"\r\n\r\n" + audio_content
                        )
            elif (req[1].find(b'/getVideo') != -1):
                video_req = req[1].split(b"id=")
                video_id = int(video_req[1])
                print(f"video_id={video_id}")
                # with open(f"lighted_christmas_tree.mp4", "rb") as video:
                with open(f"./video/{video_id}.mp4", "rb") as video:                
                    video_content = video.read()
                    response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: video/mp4\r\n"
                            b"Content-Length: " + str(len(video_content)).encode("utf-8") + b"\r\n\r\n" + video_content
                        )
        elif (req[0] == b'POST'):
            if (req[1] == b'/login'):
                login_str = request.split(b"\r\n\r\n")[1]
                login_req = json.loads(login_str.decode("utf-8"))
                account = login_req.get('account', '')
                password = login_req.get('password', '')
                print(f"account:{account}\npassword:{password}")
                if check_login_credentials(account, password):
                    login_success = b"1"
                else:
                    login_success = b"0"
                response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: text/html\r\n"
                            b"Content-Length: " + str(len(login_success)).encode("utf-8") + b"\r\n\r\n" + login_success
                        )
            elif (req[1] == b'/register'):
                reg_str = request.split(b"\r\n\r\n")[1]
                reg_req = json.loads(reg_str.decode("utf-8"))
                print(reg_req)
                account = reg_req.get('newAccount', '')
                password = reg_req.get('newPassword', '')
                print(f"account:{account}\npassword:{password}")
                if not reg_check_exist(account,password):
                    register_success = b"1"
                else: 
                    register_success = b"0"
                response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: text/html\r\n"
                            b"Content-Length: " + str(len(register_success)).encode("utf-8") + b"\r\n\r\n" + register_success
                        )
            elif (req[1] == b'/sendMessage'):
                message_str = request.split(b"\r\n\r\n")[1]
                message = json.loads(message_str.decode("utf-8"))
                if insert_message(message):
                    insert_success = b"1"
                else: 
                    insert_success = b"0"
                response = (
                        b"HTTP/1.1 200 OK\r\n"
                        b"Content-Type: text/html\r\n"
                        b"Content-Length: " + str(len(insert_success)).encode("utf-8") + b"\r\n\r\n" + insert_success
                    )
                # print(message)
            elif (req[1] == b'/upload_audio'):
                print("================================================================>")
                content_length = int(request.split(b'Content-Length: ')[1].split(b'\r')[0])
                print(content_length)
                request += receive_data(client_socket, content_length)
                message = store_audio(request)
                if insert_message(message):
                    insert_success = b"1"
                else: 
                    insert_success = b"0"
                response = (
                        b"HTTP/1.1 200 OK\r\n"
                        b"Content-Type: text/html\r\n"
                        b"Content-Length: " + str(len(insert_success)).encode("utf-8") + b"\r\n\r\n" + insert_success
                    )
            elif (req[1] == b'/upload_video'):
                print("uploading video")
                content_length = int(request.split(b'Content-Length: ')[1].split(b'\r')[0])
                print(content_length)
                request += receive_data(client_socket, content_length)
                content_type_start = request.find(b'Content-Type: multipart/form-data; boundary=') + len(b'Content-Type: multipart/form-data; boundary=')
                content_type_end = request.find(b'\r\n', content_type_start)
                boundary = request[content_type_start:content_type_end]
                # print("================================================================>")
                # print(video_content)
                message = store_video(request,boundary)
                print("successfully store video")
                if insert_message(message):
                    insert_success = b"1"
                else: 
                    insert_success = b"0"
                response = (
                        b"HTTP/1.1 200 OK\r\n"
                        b"Content-Type: text/html\r\n"
                        b"Content-Length: " + str(len(insert_success)).encode("utf-8") + b"\r\n\r\n" + insert_success
                    )
                
        # Send the response
        print("<================================================================")
        # print(response)
        client_socket.sendall(response)

    print(f"client disconnected")
    # Close the client socket
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set up server address
    server_addr = ("", PORT)
    
    # Bind the socket
    server_socket.bind(server_addr)
    
    # Listen for incoming connections
    server_socket.listen(10)

    print(f"Server listening on port {PORT}")
    try:
        while True:
            client_socket, client_addr = server_socket.accept()

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=serve_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("server disconnected")

    # Close the server socket (this code will never reach this point)
        server_socket.close()

if __name__ == "__main__":
    main()
