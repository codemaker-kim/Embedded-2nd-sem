from machine import Pin, I2C
from i2c_lcd import I2cLcd
import network
import socket
import time
import json

# 와이파이 변수
WiFi = "wifiname"
PASSWORD = ""
server_ip = "ip"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

#버튼 세팅
button = Pin(15, Pin.IN, Pin.PULL_DOWN)

#LCD 설정
i2c = I2C(0, scl=Pin(17), sda=Pin(16))
lcd = I2cLcd(i2c, 0x27, 4, 20)

#LCD 초기화
lcd.clear()
lcd.putstr("  Hello from pico!")
lcd.move_to(0, 1)
lcd.putstr("     -bed click-")

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

    response = client_socket.recv(1024).decode()
    print("Raw Response from server:")
    print(response)

    try:
        # HTTP 헤더와 본문 분리
        json_start = response.find("\r\n\r\n") + 4  # 헤더 끝 다음 위치
        json_content = response[json_start:]  # JSON 본문 추출
        print("Extracted JSON Content:", json_content)

        # JSON 파싱
        parsed_response = json.loads(json_content)
        print("Parsed Response:", parsed_response)

        # LCD 출력
        lcd.clear()
        lcd.putstr(f"    {parsed_response['state']}")
        lcd.move_to(0,1)
        if 'off' in parsed_response['state']:
            tmp = parsed_response['time'].split(', ')
            time_parse = f"{tmp[1]}-{tmp[2]} {tmp[3]}:{tmp[4]}:{tmp[5]}"
            lcd.putstr(f"Time: {time_parse}")
            lcd.move_to(0,2)
        else:
            lcd.putstr(f"Time: {parsed_response['time']}")
            lcd.move_to(0,2)
        lcd.putstr("   - Bed Click -")
    except (ValueError, KeyError) as e:
        print(f"Error parsing JSON: {e}")
        lcd.clear()
        lcd.putstr("Error: Invalid JSON")
    finally:
        client_socket.close()



# 소켓 준비
def open_socket():
    address = (server_ip, 80)
    client_socket = socket.socket()
    client_socket.connect(address)
    print(client_socket)
    return client_socket

# 리모컨 로직
try:
    while True:
        if button.value() == 1:
            connect_wifi()
            connection = open_socket()
            toggleLight(connection)
            time.sleep(0.5)
        time.sleep(0.1)

except KeyboardInterrupt:
    machine.reset()
