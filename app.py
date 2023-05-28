import base64
import json
import binascii
import subprocess
import startSupFire
from flask import Flask, request, render_template, redirect, url_for
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'NN13'
app.config['BASIC_AUTH_PASSWORD'] = 'azsxdcfv'
basic_auth = BasicAuth(app)

# Определяем имя файла и открываем его для чтения/записи
def readMainConfig():
    try:
        with open('main.json','r') as conf:
            return json.load(conf)
    except:
        with open('main.json','w') as conf:
            data = []
            json.dump(data, conf)

def decode_rules(rules):
    # Функция для декодирования правил из base64
    for rule in rules:
    	if rule['type'] == "regex" or rule['type'] == "string":
    	    rule['pattern'] = base64.b64decode(rule['pattern']).decode('utf-8')
    	elif rule['type'] == "hex":
            rule['pattern'] = binascii.hexlify(base64.b64decode(rule['pattern'])).decode('utf-8')
    return rules

def encode_rules(rules):
    # Функция для кодирования правил в base64
    for rule in rules:
        if rule['type'] == "regex" or rule['type'] == "string":
            rule['pattern'] = base64.b64encode(rule['pattern'].encode('utf-8')).decode('utf-8')
        elif rule['type'] == "hex":
            rule['pattern'] = base64.b64encode(binascii.unhexlify(rule['pattern'])).decode('utf-8') #дописать для hex
    return rules

def read_rules(file_name):
    # Функция для чтения правил из файла
    with open(file_name, 'r') as f:
        data = json.load(f)
    data['inRules'] = decode_rules(data['inRules'])
    data['outRules'] = decode_rules(data['outRules'])
    return data

def write_rules(data, file_name):
    # Функция для записи правил в файл
    data['inRules'] = encode_rules(data['inRules'])
    data['outRules'] = encode_rules(data['outRules'])
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)
        
def write_serv(data, file_name):
    # Функция для записи сервиса в файл
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
@basic_auth.required
def home():
    mainCfg = readMainConfig()
    try:
        currentService = request.args['service']
    except:
        try:
            currentService = mainCfg[0]['name']
        except:
            currentService=''
    try:
        for serv in mainCfg:
            if serv['name'] == currentService:
                data = read_rules(serv['config'])
        return render_template('home.html', data=data, services = mainCfg, current=currentService)
    # Главная страница с выводом текущих правил
    except:
        return render_template('home.html', data={}, services = mainCfg, current='')


@app.route('/add_rule', methods=['POST'])
@basic_auth.required
def add_rule():
    mainCfg = readMainConfig()
    currentService = request.form['service']
    for serv in mainCfg:
        if serv['name'] == currentService:
            data = read_rules(serv['config'])
            file_name = serv['config']
    # Добавление нового правила
    rule = {
        'pattern': request.form['pattern'],
        'occurences': int(request.form['occurences']),
        'type':request.form['type']
    }
    ruleDirection = request.form['direction']
    if ruleDirection == "in":
        data['inRules'].append(rule)
    elif ruleDirection == "out":
        data['outRules'].append(rule)
    write_rules(data, file_name)
    return redirect(url_for('home', service = currentService))


@app.route('/add_service', methods=['POST'])
@basic_auth.required
def add_service():
    data = readMainConfig()
    newServ = {
    	'name': request.form['nameS'],
    	'config': request.form['configS'],
    	'ports': request.form['portsS']
    }
    data.append(newServ)
    write_serv(data, 'main.json')
    with open(newServ['config'],'w') as new:
    	empty = {
    	    'name': newServ['name'],
    	    'inRules':[],
    	    'outRules':[]	
    	}
    	json.dump(empty, new, indent=4)
    	new.close()
    return redirect(url_for('home', service=newServ['name']))


@app.route('/startAll', methods=['POST'])
@basic_auth.required
def start():
    currentService=request.form['service']
    startSupFire.runAllFilters()
    return redirect(url_for('home', service = currentService))

@app.route('/stopAll', methods=['POST'])
@basic_auth.required
def stop():
    currentService=request.form['service']
    startSupFire.stopAllFilters()
    return redirect(url_for('home', service = currentService))

@app.route('/remove', methods=['POST'])
@basic_auth.required
def remove():
    current=request.form['current']
    ruleType=request.form['type']
    direction=request.form['direction']
    pattern=request.form['pattern']
    mainCfg=readMainConfig()
    for serv in mainCfg:
        if serv['name'] == current:
            path=serv['config']
    
    rules = read_rules(path)
    
    if direction == 'in':
        for rule in rules['inRules']:
            if rule['pattern'] == pattern and rule['type'] == ruleType:
                rules['inRules'].remove(rule)
        write_rules(rules, path)   
    elif direction == 'out':
        for rule in rules['outRules']:
            if rule['pattern'] == pattern and rule['type'] == ruleType:
                rules['outRules'].remove(rule)
        write_rules(rules, path) 
    return redirect(url_for('home', service = current))

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
