import subprocess, os
import vsql, vxml

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'



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


