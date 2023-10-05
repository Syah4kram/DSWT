from flask import Flask, render_template, jsonify, request
from waitress import serve
from datetime import datetime
import os
import json

filename = 'static/json/data.json'
listObj = []

app = Flask(__name__, static_url_path="", static_folder='static')
JSON_FOLDER = 'static/json'

@app.route('/', methods=['GET', 'POST'])
def viewdata():
    return render_template('index.html')

@app.route('/returnjson', methods = ['GET'])
def ReturnJSON():
    if(request.method == 'GET'):
        data = json.load(open('static/json/data.json'))
        return jsonify(data)
    
@app.route('/adddata', methods=['GET', 'POST'])
def AddData():
    if(request.method == 'GET'):
        with open(filename) as fp:
            listObj = json.load(fp)
        l = len(listObj['feeds'])-1

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        f1add = request.args.get('field1')
        f2add = request.args.get('field2')
        f3add = request.args.get('field3')

        listObj['feeds'].append({
            "created_at": dt_string,
            "entry_id": l+1,
            "field1": f1add,
            "field2": f2add,
            "field3": f3add
        })

        with open(filename, 'w') as json_file:
            json.dump(listObj, json_file, indent=4, separators=(',',': '))
            
        data = json.load(open('static/json/data.json'))
        return jsonify(data)

@app.route('/cleandata', methods=['GET', 'POST'])
def cleanData():
    newlistObj = ""
    nowdt = datetime.now()
    now = nowdt.timestamp()
    jsonfile=open(filename)
    listObj = json.load(jsonfile)
    l = len(listObj['feeds'])-1

    for i in range(l, -1, -1):
        jsonfile=open(filename)
        readlistObj = json.load(jsonfile)
        dt = str(readlistObj['feeds'][i]['created_at'])
        dt_string = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
        epoch = dt_string.timestamp()

        if(now-epoch > 86400):
            jsonpath = 'static/json/' + str(datetime.strftime(dt_string, "%d%m%Y")) + '.json'
            if(os.path.exists(jsonpath) == False):
                with open(jsonpath, 'w') as json_file:
                    newfile = {'feeds': []}
                    newfile['feeds'].append(readlistObj['feeds'][i])
                    json.dump(newfile, json_file, indent=4, separators=(',',': '))
            else:
                with open(jsonpath) as fp:
                    newlistObj = json.load(fp)
                
                newlistObj['feeds'].append({
                    "created_at": readlistObj['feeds'][i]['created_at'],
                    "entry_id": readlistObj['feeds'][i]['entry_id'],
                    "field1": readlistObj['feeds'][i]['field1'],
                    "field2": readlistObj['feeds'][i]['field2'],
                    "field3": readlistObj['feeds'][i]['field3']
                })
                with open(jsonpath, 'w') as json_file:
                    json.dump(newlistObj, json_file, indent=4, separators=(',',': '))
            listObj['feeds'].pop()
    
    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file, indent=4, separators=(',',': '))

    return jsonify(newlistObj)

if __name__ == '__main__':
    app.run(debug=True)
    #serve(app, host="0.0.0.0", port=5000)