from flask import Flask, request, redirect, jsonify, make_response
from flask_cors import CORS
import werkzeug.exceptions as er
import os
import time


app = Flask(__name__, static_url_path='')
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
IMG_DIR = 'test_pics'
IMG_UPLOAD = 'original'
IMG_RESULT = 'result'
IMG_ANALYSIS_AREA = os.path.join('static', 'images', 'analysis.png')

file_dir = os.path.join(basedir, IMG_DIR)


def mkpicdir():
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    if not os.path.exists(f'{file_dir}/{IMG_UPLOAD}'):
        os.makedirs(f'{file_dir}/{IMG_UPLOAD}')
    if not os.path.exists(f'{file_dir}/{IMG_RESULT}'):
        os.makedirs(f'{file_dir}/{IMG_RESULT}')


@app.route("/")
def hello():
    return app.send_static_file('index.html')


@app.route('/test')
def test():
    return 'test'


@app.route('/upload', methods=['POST'])
def upload():
    mkpicdir()
    try:
        img = request.files['img']
        img_name = img.filename
        #ext = img_name.rsplit('.',1)[1]
        now = str(int(time.time()))
        new_filename = now + '.png'
        img.save(os.path.join(file_dir, IMG_UPLOAD, new_filename))
        # return img_name

        os.system(
            command="E:/Bigsoftware/Anaconda3/envs/pytorch-gpu/python.exe ../pytorch-CycleGAN-and-pix2pix/use.py")
        return jsonify({
            'status': 200,
            'msg': new_filename
        })
    except er.BadRequestKeyError:

        return jsonify({
            'status': -100,
            'msg': er.BadRequestKeyError
        })
    except:
        return jsonify({
            'status': -999,
            'msg': 'unknown error'
        })


@app.route('/show/<string:name>', methods=['GET'])
def show(name):
    mkpicdir()
    try:
        img_name = os.path.join(file_dir, IMG_RESULT, name)
        img = open(img_name, 'rb').read()
        response = make_response(img)
        response.headers['Content-Type'] = 'image/png'
        return response
        # return img
    except:
        return 'img is not exist', 404


@app.route('/analysis/<string:name>', methods=['GET'])
def analysis(name):
    mkpicdir()
    try:
        img_name = os.path.join(basedir, IMG_ANALYSIS_AREA)
        # print(img_name)
        img = open(img_name, 'rb').read()
        response = make_response(img)
        response.headers['Content-Type'] = 'image/png'
        return response
        # return img
    except:
        return 'img is not exist', 404


@app.route('/score', methods=['POST'])
def score():
    filename = request.form.get('filename')
    person = request.form.get('person')
    score = request.form.get('score')
    score = str(person) + '-' + str(score)
    scores = {}
    with open('score.txt') as f:
        for line in f:
            arr = line.split(' ')
            if len(arr) == 2:
                scores[arr[0]] = arr[1]
                #scores[name] = s

    scores[filename] = score
    with open('score.txt', 'w+') as f:
        for name, s in scores.items():
            f.write('{} {}'.format(name, s))

        f.write('\n')

    return '评分成功', 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
