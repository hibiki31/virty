import subprocess, os
import vsql

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

def NodeInit(PBNAME,EXVALUE):
    if PBNAME == "gluster":
        cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_init_gluster.yml -i  ' + SPATH + '/ansible/host_node.ini --extra-vars ' + EXVALUE
        subprocess.check_call(cmd, shell=True)
    elif PBNAME == "libvirt":
        cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_init_libvirt.yml -i  ' + SPATH + '/ansible/host_node.ini'
        subprocess.check_call(cmd, shell=True)	
    elif PBNAME == "frr":
        cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_init_frr.yml -i  ' + SPATH + '/ansible/host_node.ini'
        subprocess.check_call(cmd, shell=True)

def AnsibleFiledeleteInnode(NODEIP,FILE):
	AnsibleNodelistInit()
	exvar = ' "file=' + FILE  + ' host=' + NODEIP + '"'
	cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_deleteinnode.yml -i  ' + SPATH + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def AnsibleFilecpInnode(NODEIP,CP,TO):
	AnsibleNodelistInit()
	print(NODEIP + CP + TO)
	exvar = ' "cp=' + CP  + ' host=' + NODEIP + ' to=' + os.path.basename(TO) + ' dir=' + os.path.dirname(TO) + '/"'
	print(exvar)
	cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_cpinnode.yml -i  ' + SPATH + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def AnsibleFilecpTonode(NODEIP,CP,TO):
	AnsibleNodelistInit()
	exvar = ' "cp=' + CP  + ' host=' + NODEIP + ' to=' + os.path.basename(TO) + ' dir=' + os.path.dirname(TO) + '/"'
	cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_cptonode.yml -i  ' + SPATH + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def	AnsibleNodelistInit():
	NODE_DATAS = vsql.SqlGetAll("kvm_node")
	nodeiplist = []
	for node in NODE_DATAS:
		nodeiplist.append(node[1] + "\n")
	f = open(SPATH + '/ansible/host_node.ini','w')
	f.writelines(nodeiplist)
	f.close()


