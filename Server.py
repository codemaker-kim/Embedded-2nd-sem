import socket
from machine import Pin, PWM, Timer, I2C, ADC
import time
from time import sleep_ms
import network
import urequests
import ujson

# 서버 코드 - 서보 처리
WiFi = "WIFI_NAME"
PASSWORD = "PW"
DB_SERVER_URL = "DB_SERVER_URL"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# GPIO 기준 핀 번호
servo1 = PWM(Pin(15))  # GPIO 16번 핀에 연결
servo2 = PWM(Pin(16))

# 서보 모터의 PWM 주파수 설정 (50Hz)
servo1.freq(50)
servo2.freq(50)

# 듀티 사이클 값 설정 (0도, 45도)
duty_start_deg = 1310  # 0도에 해당하는 값 (MG996R 기준)
duty_return_deg = 8200  # 45도에 해당하는 값 (MG996R 기준)
duty_stop_deg = 4755


# 와이파이 연결하기
def connect():
    if not wlan.isconnected():
        wlan.connect(WiFi, PASSWORD)
        print("Waiting for Wi-Fi connection", end="...")
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)
    try:
        ip = wlan.ifconfig()[0]
        print("\nPico IP Address:", ip)
        return ip
    except Exception as e:
        print("Error retrieving IP configuration:", e)
        return None

# 소켓 열기
def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

# 웹서버 구축
def WebServer(connection):
    while True:
        client = connection.accept()[0]
        print(f"Client connected from {client}")
        try:
            request = client.recv(1024).decode()
            print("Request received:", request)

            response_content = ujson.dumps(handle_request(request))
            print(response_content)

            # HTTP 응답 형식 구축
            # 문자열 내 탭도 포함되서 정렬이 이렇다
            response = f"""HTTP/1.1 200 OK\r\n
"Content-Type": "application/json"\r\n
"Content-Length": {len(response_content)}\r\n
"Connection": "close"\r\n\r\n
{response_content}"""

            client.send(response.encode())
        except Exception as e:
            print("Error while handling request:", e)
        finally:
            client.close()


# 클라이언트 측에서 그냥 Toggle
def handle_request(request):
    # 요청 처리 나중에 조건 처리 수정 필요
    if "/toggle" in request:
        state = toggleLight()
        if state == "on":
            servo1.duty_u16(duty_start_deg)
            servo2.duty_u16(duty_start_deg)
            time.sleep(0.5)  # 모터가 0도로 이동할 수 있도록 잠시 대기

            # 서보 모터를 시계방향으로 45도로 설정
            servo1.duty_u16(duty_stop_deg)
            servo2.duty_u16(duty_stop_deg)

        elif state == "off":
            # 서보 모터를 반시계방향으로 다시 0도로 되돌리기
            servo1.duty_u16(duty_return_deg)
            servo2.duty_u16(duty_return_deg)
            sleep(0.5)  # 모터가 원래 위치로 되돌아갈 수 있도록 잠시 대기

            servo1.duty_u16(duty_stop_deg)
            servo2.duty_u16(duty_stop_deg)

        response = {"state": f"Light is {state}!",
                    "message": f"Successfully {state}."}
        return response
    else:
        return {"Error": "Fail to toggle Light."}


def toggleLight():
    request = urequests.get(DB_SERVER_URL + ".json").json()
    lightState = request['state']

    # 나중에 모터 각도 조절하는 로직으로 바꾸는 것 필요
    if lightState == "on":
        toggleTime = time.localtime()
        data = {"state": "off", "toggleTime": f"{toggleTime}"}
        urequests.patch(DB_SERVER_URL + ".json", json=data)
        print("Send Light off Request!")
        return "off"
    elif lightState == "off":
        toggleTime = time.localtime()
        beforeUseLightTime = urequests.get(DB_SERVER_URL + ".json").json()['toggleTime']

        beforeUseLightTime = eval(beforeUseLightTime)

        offTime = calc_timeDifference(toggleTime, beforeUseLightTime)

        data = {"state": "on", "toggleTime": f"{toggleTime}"}
        urequests.patch(DB_SERVER_URL + ".json", json=data)
        print("Send Light On Request!")
        print("Off time: ", offTime)
        return "on"
    else:
        toggleTime = time.localtime()
        data = {"state": "on", "toggleTime": f"{toggleTime}"}
        urequests.post(DB_SERVER_URL + ".json", json=data)
        return "on"


# 스위치 켜고 껏을 때 시간 차이 계산 출력
def calc_timeDifference(toggleTime, beforeUseLightTime):
    timestamp1 = time.mktime(toggleTime)
    timestamp2 = time.mktime(beforeUseLightTime)

    time_difference = timestamp1 - timestamp2

    hours = 0
    minutes = 0

    if time_difference >= 3600:
        hours = time_difference / 3600
        time_difference = time_difference - (3600 * hours)

    if time_difference >= 60:
        minutes = time_difference / 60
        time_difference = time_difference - (60 * minutes)

    return f"{hours}: {minutes} : {time_difference}"


try:
    ip = connect()
    connection = open_socket(ip)
    WebServer(connection)
except KeyboardInterrupt:
    machine.reset()
