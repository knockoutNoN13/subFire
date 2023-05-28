import subprocess
import time
import json
import os

def runWeb():
    proc = subprocess.Popen(["python3", "app.py", '&'])
    with open('pids.txt', 'w') as pid:
        pid.write("web: " + str(proc.pid)+'\n')
        pid.close()
    
def runFilter(fileName, ports):
    proc = subprocess.Popen(["python3", "filter.py", fileName, ports, '&'])
    with open('pids.txt', 'a') as pid:
        pid.write("filter: " + str(proc.pid)+'\n')
        pid.close()

def runAllFilters():
    with open('pids.txt','r') as f:
        for line in f:
            if "web" in line:
                web=line
                f.close()
                break
    with open('pids.txt','w') as f:
        f.write('')
        f.close()
    with open('main.json','r') as main:
        f = json.load(main)
        for serv in f:
            runFilter(serv['config'], serv['ports'])
        main.close()
    f = open('pids.txt','a')
    f.write(web)

def stopAllFilters():
    try:
        with open('pids.txt','r') as processes:
            for line in processes:
                proc = line.split(' ')
                if proc[0] == 'filter:':
                    os.system('kill -9 {}'.format(proc[1]))
    except:
        pass

if __name__ == "__main__":
    runWeb()
    time.sleep(5)
    runAllFilters()

