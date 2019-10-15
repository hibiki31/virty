def VirtyStorageAddHelp():
	print("\
	virty storage add archive NODE01 ssd dir /kvm/archive\n")
	

def VirtyDomMakeHelp():
	print("\
	virty dom make base vm010 1024 2 auto pass \n \
	virty dom make nic bridge vm010 virbr1 \n \
	virty dom make img vm010 storage_vm CentOS7-1810 \n \
	virty dom define static vm010 Chinon \n")
	

def VirtyDomMakeBaseHelp():
	print("\nHOW.")
	print("   virty dom make base (DomainNAME) (MEMORY) (CORE) (VNC_PORT) (VNCPassword)")
	print("\nEX.")
	print("   virty dom make base vm001 1024 2 auto Password\n‬")	
	

def VirtyDomMakeNicHelp():
	print("\nHOW.")
	print("   virty dom make nic bridge (DomainNAME) (SOURCE)")
	print("\nEX.")
	print("   virty dom make nic bridge vm001 virbr0\n‬")	
	

def VirtyNodeAddHelp():
	print("\n It is necessary to be able to connect with SSH in order to get memory and CPU information.")
	print("\nHOW.")
	print("   virty node add (NAME) (IP/DOMAIN)")
	print("\nEX.")
	print("   virty node add node01 192.168.0.1\n‬")
	

def VirtyDomainMakeNomalHelp():
	print("\nHOW.")
	print("   virty dom make nomal (ArchiveNAME) (DomainNAME) (BridgeAddr) (VNCPASS) (MEMORY) (CORE) (POOL)")
	print("\nEX.")
	print("   virty dom make nomal CentOS chinon vm001 virbr0 5900 1024 2 none\n‬")	
	

def VirtyHelp():
	print("\
	virty archive\n\
	virty storage\n\
	virty dom\n\
	virty develop \n\
	virty dom autostart CentOS_Virty \n\
	virty network \n\
	virty node \n\
 	")