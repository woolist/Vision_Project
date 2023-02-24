"""
Simple app to upload an image via a web form 
and view the inference results on the image in the browser.
"""

# https://docs.ultralytics.com/tutorials/pytorch-hub/

# https://github.com/ultralytics/yolov5/issues/36

import argparse
import io
import os
import json
import glob
from PIL import Image
from uuid import uuid4
import torch
from flask import Flask, render_template, request, redirect, url_for, session
from ast import literal_eval
import collections
import numpy as np
import sys

# 폴더안의 파일 삭제 함수
def DeleteAllFiles(filePath):
    if os.path.exists(filePath):
        for file in os.scandir(filePath):
            os.remove(file.path)
 
app = Flask(__name__)



@app.route("/detect", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        DeleteAllFiles('C:/Users/admin/project3/project/project3/project3/static/aft')  #파일 업로드 후 새로 검사 시작할 때마다 폴더 내 파일 삭제
        DeleteAllFiles('C:/Users/admin/project3/project/project3/project3/static/bef')  # 경로설정필요
        
        # 다중파일 업로드
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files.getlist("file")
        if not file:
            return
        
        resultlist=[]
        pf=[]
        for file in file:
            filename = file.filename.rsplit("/")[0]     #파일경로에서 파일명만 추출
            print("진행 중 파일 :", filename)

            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes))
            # print(img)
            img.save(f"static/bef/{filename}", format="JPEG")
            print('원본 저장')

            results = model(img, size=640)
            results_list = results.pandas().xyxy[0].to_json(orient="records")
            results_list = literal_eval(results_list)
            classes_list = [item["name"] for item in results_list]
            result_counter = collections.Counter(classes_list)
            
            results.render()  # results.imgs에 바운딩박스와 라벨 처리

            for img in results.ims:
                img_base64 = Image.fromarray(img)
                img_base64.save(f"static/aft/{filename}", format="JPEG")
                print('디텍트 저장')

            resultlist.append(json.dumps(dict(result_counter)))

            data = results.pandas().xyxy[0][['name']].values.tolist()   # results.imgs의 name값만 가져오기
            print("데이터:",data)

            if len(data) == 0:
                pf.append("PASS")    # data 리스트의 값이 0이면 양품으로 pass
            if len(data) != 0:
                pf.append("FAIL")    # data 리스트의 값이 0이 아니면 불량으로 fail
            
            root = "static/aft"
            if not os.path.isdir(root):      #파일명 리스트로 저장
                return "Error : not found!"
            files = []
            for file in glob.glob("{}/*.*".format(root)):
                fname = file.split(os.sep)[-1]
                files.append(fname)
            print("파일스 :",files)
            
            if len(files)>0:
                firstimage = "static/aft/"+files[0]
            else: pass

            datanum = len(pf)
            rate = round(pf.count('PASS') / len(pf), 3)
            correct = pf.count('PASS')
            
            print(resultlist)
        return render_template("imageshow.html",files=files,resultlist=resultlist, pf=pf,datanum=datanum,rate=rate,correct=correct,
                                firstimage=firstimage,enumerate=enumerate,len=len, results_list=results_list)
    return render_template("detect.html")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/description')
def description():
    return render_template('description.html')

@app.route('/labels')
def labels():
    return render_template('labels.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask app exposing yolov5 models")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    args = parser.parse_args()

# local model
    model = torch.hub.load(
        'ultralytics/yolov5', 'custom', 'yolov5l-best-230214.pt', autoshape=True,
    )
    model.eval()

    flask_options = dict(
        host='0.0.0.0',
        debug=True,
        port=args.port,
        threaded=True,
    )

    app.run(**flask_options)