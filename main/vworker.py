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

    # quer = subprocess.run(["python3","queuer.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)




    # quer = subprocess.Popen(["python3", "queuer.py"],)

    # if not quer.wait() == 0:
    #     virty.vsql.QueueUpdate(que[0],"error","Queue error")


    
    path_err = SPATH + '/log/queue-err' + str(que[0]) + '.log'
    path_out = SPATH + '/log/queue-out' + str(que[0]) + '.log'

    with open(path_err, mode='w') as f_err:
        with open(path_out, mode='w') as f_out:
            quer = subprocess.run(["python3","queuer.py"], stderr=f_err, stdout=f_out, cwd=SPATH)
            if quer.returncode != 0:
                virty.vsql.QueueUpdate(que[0],"error","Queue error")
    
    

    time_end = time()
    time_run = time_end - time_start
    virty.vsql.QueueUpdateTime(que[0],time_run)
    print("Finish "+str(time_run) + " s")