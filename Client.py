from machine import Pin
import network
import socket
import time

WiFi = "SmuWiFi_Free"
PASSWORD = "password"
server_ip = "server_ip"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# 와이파이 연결
def connect_wifi():
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WiFi, )
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)
    print("\nConnected to WiFi!")
    print("IP Address:", wlan.ifconfig()[0])


# 서버에 요청 보내기
def toggleLight(client_socket):
    endpoint = "toggle"
    request = f"GET /{endpoint} HTTP/1.1\r\n"
    f"Host: {server_ip}\r\n"
    f"Connection: keep-alive\r\n"
    f"User-Agent: Python-HTTP-Client\r\n"
    f"\r\n"
    print("Sending request:", request)
    client_socket.send(request.encode())

    response = client_socket.recv(1024)
    print("Response from server:")
    print(response.decode())

    client_socket.close()


# 소켓 준비
def open_socket():
    address = (server_ip, 80)
    client_socket = socket.socket()
    client_socket.connect(address)
    print(client_socket)
    return client_socket

# 리모컨 버튼 세팅
try:
    button = Pin(15, Pin.IN, Pin.PULL_DOWN)
    while True:
        if button.value() == 1:
            connect_wifi()
            connection = open_socket()
            toggleLight(connection)
            time.sleep(0.5)
        time.sleep(0.1)

except KeyboardInterrupt:
    machine.reset()
