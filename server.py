#!/usr/bin/env python
from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import cv2

# Define a counter metric
counter_metric = Counter('microsample_calls_total', 'Total calls to microsampl api (counter)')

__info = {
    'name': 'Ramin Dehghan',
    'email': 'online@wolog.org',
    'title': 'dev'
}

info = __info

# Define stream capture
def get_frame():
    camera=cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 426)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


application = Flask(__name__)

@application.route('/')
def index():
    counter_metric.inc()
    return "Functional"


# Show info
@application.route('/api/info', methods=['GET'])
def get_info():
    # Increase counter to 
    counter_metric.inc()
    return jsonify(info)


# Provide dummy metrics for prometheus
@application.route('/metrics')
def metrics():
    
    # Generate the latest metrics in Prometheus format
    prometheus_metrics = generate_latest()

    return Response(prometheus_metrics, mimetype=CONTENT_TYPE_LATEST)


# Stream video
@application.route('/video')
def video():
     counter_metric.inc()
     return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


def main():
    application.run()


if __name__ == '__main__':
    application.run()
