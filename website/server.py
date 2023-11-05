from flask import Flask, render_template, send_file, jsonify, request
from waitress import serve
from datetime import datetime, timedelta
import os
import json
import pandas as pd
import numpy as np

filename = 'D:/termometer-air/static/json/data.json'
listObj = []

app = Flask(__name__, static_url_path="", static_folder='static')
JSON_FOLDER = 'D:/termometer-air/static/json'

@app.route('/', methods=['GET'])
def viewdata():
    return render_template('index.html')

@app.route('/download', methods=['GET'])
def viewdownload():
    return render_template('download.html')

@app.route('/returnjson', methods = ['GET'])
def ReturnJSON():
    if(request.method == 'GET'):
        data = json.load(open('D:/termometer-air/static/json/data.json'))
        return jsonify(data)
    
@app.route('/adddata', methods=['GET'])
def AddData():
    if(request.method == 'GET'):
        with open(filename) as fp:
            listObj = json.load(fp)
        l = len(listObj['feeds'])-1

        now = datetime.utcnow()
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
            
        data = json.load(open('D:/termometer-air/static/json/data.json'))
        newlistObj = ""
        nowdt = datetime.utcnow()
        now = nowdt.timestamp()
        jsonfile=open(filename)
        listObj = json.load(jsonfile)

        
        jsonfile=open(filename)
        readlistObj = json.load(jsonfile)
        dt = str(readlistObj['feeds'][0]['created_at'])
        dt_string = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
        epoch = dt_string.timestamp()

        if(now-epoch > 86400):
            jsonpath = 'D:/termometer-air/static/json/' + str(datetime.strftime(dt_string, "%d%m%Y")) + '.json'
            if(os.path.exists(jsonpath) == False):
                with open(jsonpath, 'w') as json_file:
                    newfile = {'feeds': []}
                    newfile['feeds'].append(readlistObj['feeds'][0])
                    json.dump(newfile, json_file, indent=4, separators=(',',': '))
            else:
                with open(jsonpath) as fp:
                    newlistObj = json.load(fp)
                    
                newlistObj['feeds'].append({
                    "created_at": readlistObj['feeds'][0]['created_at'],
                    "entry_id": readlistObj['feeds'][0]['entry_id'],
                    "field1": readlistObj['feeds'][0]['field1'],
                    "field2": readlistObj['feeds'][0]['field2'],
                    "field3": readlistObj['feeds'][0]['field3']
                })
                with open(jsonpath, 'w') as json_file:
                    json.dump(newlistObj, json_file, indent=4, separators=(',',': '))
            listObj['feeds'].pop(0)
        
        with open(filename, 'w') as json_file:
            json.dump(listObj, json_file, indent=4, separators=(',',': '))

        return jsonify(data)

@app.route('/cleardata', methods=['GET'])
def clearData():
    if(request.method == 'GET'):
        data = json.load(open('D:/termometer-air/static/json/data.json'))
        newlistObj = ""
        nowdt = datetime.utcnow()
        now = nowdt.timestamp()
        jsonfile=open(filename)
        listObj = json.load(jsonfile)

        
        jsonfile=open(filename)
        readlistObj = json.load(jsonfile)
        dt = str(readlistObj['feeds'][0]['created_at'])
        dt_string = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
        epoch = dt_string.timestamp()

        if(now-epoch > 86400):
            jsonpath = 'D:/termometer-air/static/json/' + str(datetime.strftime(dt_string, "%d%m%Y")) + '.json'
            if(os.path.exists(jsonpath) == False):
                with open(jsonpath, 'w') as json_file:
                    newfile = {'feeds': []}
                    newfile['feeds'].append(readlistObj['feeds'][0])
                    json.dump(newfile, json_file, indent=4, separators=(',',': '))
            else:
                with open(jsonpath) as fp:
                    newlistObj = json.load(fp)
                    
                newlistObj['feeds'].append({
                    "created_at": readlistObj['feeds'][0]['created_at'],
                    "entry_id": readlistObj['feeds'][0]['entry_id'],
                    "field1": readlistObj['feeds'][0]['field1'],
                    "field2": readlistObj['feeds'][0]['field2'],
                    "field3": readlistObj['feeds'][0]['field3']
                })
                with open(jsonpath, 'w') as json_file:
                    json.dump(newlistObj, json_file, indent=4, separators=(',',': '))
            listObj['feeds'].pop(0)
        
        with open(filename, 'w') as json_file:
            json.dump(listObj, json_file, indent=4, separators=(',',': '))

        return jsonify(data)

@app.route('/returnjsonbydate', methods=['GET'])
def returnJSONByDate():
    if(request.method == 'GET'):
        startdate = str(request.args.get('sd'))
        enddate = str(request.args.get('ed'))
        
        files = [f for f in os.listdir(JSON_FOLDER)]
        alljson = json.loads('{"feeds": []}')

        for i in range(0, len(files)):
            thisfile = files[i]
            jsonpath = os.path.join(JSON_FOLDER, thisfile)
            with open(jsonpath) as fp:
                newlistObj = json.load(fp)
            
            for i in range(0, len(newlistObj['feeds'])):
                dt = datetime.strptime(newlistObj['feeds'][i]['created_at'], "%Y-%m-%dT%H:%M:%SZ")

                fromdate = datetime.strptime(startdate, '%Y-%m-%d')
                todate   = datetime.strptime(enddate, '%Y-%m-%d')

                if dt >= fromdate and dt <= todate+timedelta(days=1):
                    alljson['feeds'].append({
                        "created_at": newlistObj['feeds'][i]['created_at'],
                        "entry_id": newlistObj['feeds'][i]['entry_id'],
                        "field1": newlistObj['feeds'][i]['field1'],
                        "field2": newlistObj['feeds'][i]['field2'],
                        "field3": newlistObj['feeds'][i]['field3']
                    })
        
        return jsonify(alljson)

@app.route('/downloadjsonbydate', methods=['GET'])
def downloadJSONByDate():
    if(request.method == 'GET'):
        startdate = str(request.args.get('sd'))
        enddate = str(request.args.get('ed'))
        
        files = [f for f in os.listdir(JSON_FOLDER)]
        alljson = json.loads('{"feeds": []}')

        for i in range(0, len(files)):
            thisfile = files[i]
            jsonpath = os.path.join(JSON_FOLDER, thisfile)
            with open(jsonpath) as fp:
                newlistObj = json.load(fp)
            
            for i in range(0, len(newlistObj['feeds'])):
                dt = datetime.strptime(newlistObj['feeds'][i]['created_at'], "%Y-%m-%dT%H:%M:%SZ")

                fromdate = datetime.strptime(startdate, '%Y-%m-%d')
                todate   = datetime.strptime(enddate, '%Y-%m-%d')

                if dt >= fromdate and dt <= todate+timedelta(days=1):
                    alljson['feeds'].append({
                        "created_at": newlistObj['feeds'][i]['created_at'],
                        "entry_id": newlistObj['feeds'][i]['entry_id'],
                        "field1": newlistObj['feeds'][i]['field1'],
                        "field2": newlistObj['feeds'][i]['field2'],
                        "field3": newlistObj['feeds'][i]['field3']
                    })
        filename = 'D:/termometer-air/static/download/download.json'
        with open(filename, 'w') as json_file:
            json.dump(alljson, json_file, indent=4, separators=(',',': '))
        return send_file(filename, as_attachment=True)

@app.route('/downloaddaily', methods=['GET'])
def downloadDaily():
    alldt  = []
    allt7  = []
    allt13 = []
    allt17 = []
    alltmax= []
    alltmin= []
    
    if(request.method == 'GET'):
        startdate = str(request.args.get('sd'))
        enddate = str(request.args.get('ed'))
        fromdate = datetime.strptime(startdate, '%Y-%m-%d')
        todate = datetime.strptime(enddate, '%Y-%m-%d')
        rangeday = todate-fromdate
        
        files = [f for f in os.listdir(JSON_FOLDER)]
        alljson = json.loads('{"feeds": []}')

        for j in range(0, len(files)):
            thisfile = files[j]
            jsonpath = os.path.join(JSON_FOLDER, thisfile)
            with open(jsonpath) as fp:
                newlistObj = json.load(fp)
            
            for i in range(0, len(newlistObj['feeds'])):
                dt = datetime.strptime(newlistObj['feeds'][i]['created_at'], "%Y-%m-%dT%H:%M:%SZ")

                fromdate = datetime.strptime(startdate, '%Y-%m-%d')
                todate   = datetime.strptime(enddate, '%Y-%m-%d')

                if dt >= fromdate and dt <= todate+timedelta(days=1):
                    alljson['feeds'].append({
                        "created_at": newlistObj['feeds'][i]['created_at'],
                        "entry_id": newlistObj['feeds'][i]['entry_id'],
                        "field1": newlistObj['feeds'][i]['field1'],
                        "field2": newlistObj['feeds'][i]['field2'],
                        "field3": newlistObj['feeds'][i]['field3']
                    })
        
        date = datetime.strptime(alljson['feeds'][0]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        for i in range(0, len(alljson['feeds'])):
            dt = datetime.strptime(alljson['feeds'][i]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            if dt < date:
                date = dt
        
        for d in range(0, rangeday.days+1):
            days = date+timedelta(days=d)
            daysbefore = days-timedelta(days=1)
            t7 = 0
            t13 = 0
            t17 = 0
            tmax = float(-127)
            tmin = float(100)
            dday = ''
            dmonth = ''
            dyear = ''
            for i in range(0, len(alljson['feeds'])):
                thisdate = datetime.strptime(alljson['feeds'][i]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                if thisdate.month == days.month:
                    if thisdate.day == daysbefore.day:
                        if thisdate.hour == 23 and thisdate.minute > 5 and thisdate.minute <= 10: t7 = float(alljson['feeds'][i]['field1'])
                    if thisdate.day == days.day:
                        if thisdate.hour == 5 and thisdate.minute > 5 and thisdate.minute <= 10: t13 = float(alljson['feeds'][i]['field1'])
                        if thisdate.hour == 9 and thisdate.minute > 5 and thisdate.minute <= 10: t17 = float(alljson['feeds'][i]['field1'])
                        if tmax < float(alljson['feeds'][i]['field2']): tmax = float(alljson['feeds'][i]['field2'])
                        if tmin > float(alljson['feeds'][i]['field3']): tmin = float(alljson['feeds'][i]['field3'])
                        if thisdate.day < 10:
                            dday = '0'+str(thisdate.day)
                        else:
                            dday = str(thisdate.day)
                        if thisdate.month < 10:
                            dmonth = '0'+str(thisdate.month)
                        else:
                            dmonth = str(thisdate.month)
                        dyear = str(thisdate.year)
                        td = dday+'-'+dmonth+'-'+dyear

            alldt.append(td)
            allt7.append(t7)
            allt13.append(t13)
            allt17.append(t17)
            alltmax.append(tmax)
            alltmin.append(tmin)

        data = pd.DataFrame({'Tanggal': alldt, 'Suhu jam 07.10': allt7, 'Suhu jam 13.10': allt13, 'Suhu jam 17.10': allt17, 'Suhu maks': alltmax, 'Suhu min': alltmin})
        data.to_csv('D:/termometer-air/static/download/daily.csv', sep=';', index=False)
        return send_file('D:/termometer-air/static/download/daily.csv', as_attachment=True)

if __name__ == '__main__':
    #app.run(debug=True)
    serve(app, host="192.168.1.249", port=5000)