import json
import subprocess
from time import sleep
from time import time
import setting
import virty
import model


while True:
    que = model.raw_fetchall("select * from queue where status =?",["init"])
    if que == None or que == []:
        sleep(1)
        virty.DomainListInit()
        continue
    time_start = time()
    que = que[0]
    try:
        POST = json.loads(que['json'])
    except:
        virty.vsql.QueueUpdate(que['id'],"error","Can't read json.")
        continue
    
    print("Found "+que['object']+" "+que['method'])
    virty.vsql.QueueUpdate(que['id'],"running","")

    # quer = subprocess.run(["python3","queuer.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # quer = subprocess.Popen(["python3", "queuer.py"],)

    # if not quer.wait() == 0:
    #     virty.vsql.QueueUpdate(que[0],"error","Queue error")


    
    path_err = setting.scriptPath + '/log/queue_' + str(que['id']) + '_err.log'
    path_out = setting.scriptPath + '/log/queue_' + str(que['id']) + '_out.log'

    with open(path_err, mode='w') as f_err:
        with open(path_out, mode='w') as f_out:
            quer = subprocess.run(["python3","module/queuer.py"], stderr=f_err, stdout=f_out, cwd=setting.scriptPath)
            if quer.returncode != 0:
                virty.vsql.QueueUpdate(que['id'],"error","Exception occurred")
    
    

    time_end = time()
    time_run = time_end - time_start
    virty.vsql.QueueUpdateTime(que['id'],time_run)
    print("Finish "+str(time_run) + " s")