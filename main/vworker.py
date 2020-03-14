import virty
import ast, subprocess
from time import sleep,time

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

while True:
    que = virty.vsql.SqlQueuget("init")
    if que == None or que == []:
        sleep(3)
        virty.DomainListInit()
        continue
    time_start = time()
    que = que[0]
    POST = ast.literal_eval(que[5])
    print("Found "+que[3]+" "+que[4])
    virty.vsql.QueueUpdate(que[0],"running","")
    quer = subprocess.Popen(["python3", "/root/virty/main/queuer.py"])

    if not quer.wait() == 0:
        virty.vsql.QueueUpdate(que[0],"error","Queue error")
    
    time_end = time()
    time_run = time_end - time_start
    print(str(time_run) + " s")
    virty.vsql.QueueUpdateTime(que[0],time_run)