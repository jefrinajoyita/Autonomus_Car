from flask import Flask, render_template
from flask_socketio import SocketIO
import eventlet
import numpy as np
from keras.models import load_model
import base64
from io import BytesIO
from PIL import Image
import cv2

app = Flask(__name__)
socketio = SocketIO(app)

speed_limit = 10

def img_preprocess(img):
    img = img[60:135, :, :]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img / 255
    return img

@socketio.on('telemetry')
def telemetry(data):
    sid = request.sid
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0 - speed / speed_limit
    print('{} {} {}'.format(steering_angle, throttle, speed))
    send_control(sid, steering_angle, throttle)

@socketio.on('connect')
def connect():
    sid = request.sid
    print(f'Connected: {sid}')
    send_control(sid, 0, 0)

def send_control(sid, steering_angle, throttle):
    socketio.emit('steer', {
        'steering_angle': str(steering_angle),
        'throttle': str(throttle)
    }, room=sid)

if __name__ == '__main__':
    model = load_model('model.h5')
    socketio.run(app, host='0.0.0.0', port=4567)
