import setting
import subprocess, os
import vsql


def NodeInit(PBNAME,EXVALUE):
    if PBNAME == "gluster":
        cmd = 'ansible-playbook ' + setting.scriptPath + '/ansible/pb_init_gluster.yml -i  ' + setting.scriptPath + '/ansible/host_node.ini --extra-vars ' + EXVALUE
        subprocess.check_call(cmd, shell=True)
    elif PBNAME == "libvirt":
        cmd = 'ansible-playbook ' + setting.scriptPath + '/ansible/pb_init_libvirt.yml -i  ' + setting.scriptPath + '/ansible/host_node.ini'
        subprocess.check_call(cmd, shell=True)	
    elif PBNAME == "frr":
        cmd = 'ansible-playbook ' + setting.scriptPath + '/ansible/pb_init_frr.yml -i  ' + setting.scriptPath + '/ansible/host_node.ini'
        subprocess.check_call(cmd, shell=True)

def AnsibleFiledeleteInnode(NODEIP,FILE):
	AnsibleNodelistInit()
	exvar = ' "file=' + FILE  + ' host=' + NODEIP + '"'
	cmd = 'ansible-playbook ' + setting.scriptPath + '/ansible/pb_deleteinnode.yml -i  ' + setting.scriptPath + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def AnsibleFilecpInnode(NODEIP,CP,TO):
	AnsibleNodelistInit()
	print(NODEIP + CP + TO)
	exvar = ' "cp=' + CP  + ' host=' + NODEIP + ' to=' + os.path.basename(TO) + ' dir=' + os.path.dirname(TO) + '/"'
	print(exvar)
	cmd = 'ansible-playbook ' + setting.scriptPath + '/ansible/pb_cpinnode.yml -i  ' + setting.scriptPath + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def AnsibleFilecpTonode(NODEIP,CP,TO):
	AnsibleNodelistInit()
	exvar = ' "cp=' + CP  + ' host=' + NODEIP + ' to=' + os.path.basename(TO) + ' dir=' + os.path.dirname(TO) + '/"'
	cmd = 'ansible-playbook ' + setting.scriptPath + '/ansible/pb_cptonode.yml -i  ' + setting.scriptPath + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def	AnsibleNodelistInit():
	NODE_DATAS = vsql.SqlGetAll("node")
	nodeiplist = []
	for node in NODE_DATAS:
		nodeiplist.append(node[1] + "\n")
	f = open(setting.scriptPath + '/ansible/host_node.ini','w')
	f.writelines(nodeiplist)
	f.close()


