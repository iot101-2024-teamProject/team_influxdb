import sys
import requests
import paho.mqtt.client as mqtt

server = "192.168.0.248"
token = "FIP2d7CTPME5ewRbgiN8qdnJqkhpK6K-RjLNIiwe9BGMKa8zoaUPE1Y6Mic3qg3WHqq6VjxuOPkTKkgTNlcKEg=="
headers = {
    "Authorization": f"Token {token}"
}

def on_connect(client, userdata, flags, rc):
    print("Connected with RC : " + str(rc))
    for topic in topics.keys():
        client.subscribe(topic)

topics = {
    # Livingroom
    "id/semicon/door/servo/control": {"location": "livingroom", "key": "control"},
    "id/semicon/door/button/info": {"location": "livingroom", "key": "btn_press"},
    "id/semicon/livingroom/dht22/temperature": {"location": "livingroom", "key": "temp"},
    "id/semicon/livingroom/dht22/humidity": {"location": "livingroom", "key": "humi"},
    "id/semicon/livingroom/bh1750/lux": {"location": "livingroom", "key": "lux"},
    "id/semicon/livingroom/step/control": {"location": "livingroom", "key": "control_stepper"},

    # Bathroom
    "id/semicon/bathroom/dht22/humidity": {"location": "bathroom", "key": "humidity"},
    "id/semicon/bathroom/dht22/temperature": {"location": "bathroom", "key": "temperature"},
    "id/semicon/bathroom/motor/control": {"location": "bathroom", "key": "control_motor"},

    # Yard
    "id/semicon/yard/NeoPixel/control": {"location": "yard", "key": "control_neopixel"},
    "id/semicon/yard/fsr402/press": {"location": "yard", "key": "press"},
    "id/semicon/yard/RFID/tag": {"location": "yard", "key": "tag"},
    "id/semicon/yard/ultrasonic/distance": {"location": "yard", "key": "distance"}
}

URL = f"http://127.0.0.1:8086/write?db=bucket01"

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    try:
        # 페이로드를 숫자로 변환
        value = float(payload)
    except ValueError:
        # 숫자가 아닌 메시지 처리: "on", "off" 또는 기타 값을 0 또는 1로 변환
        if payload.lower() in ["tag", "open", "ON", "up", "box", "door", "btn_press"]:
            value = 1.0
        elif payload.lower() in ["untag", "close", "OFF", "down", "shutdown", "release"]:
            value = 0.0
        else:
            print(f"Unsupported non-numeric payload: {payload} from {msg.topic}")
            return  # 처리할 수 없는 메시지는 무시
    topic_info = topics.get(msg.topic)
    if topic_info is None:
        print(f"Unknown topic: {msg.topic}")
        return
    location = topic_info["location"]
    key = topic_info["key"]
    d = f"ambient,location={location} {key}={value}"
    r = requests.post(url=URL, data=d, headers=headers)
    print(f'rc : {r.status_code} for {msg.topic:38} {value: >5.1f}')

client = mqtt.Client()
client.connect(server, 1883, 60)
client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
