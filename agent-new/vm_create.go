package main

import (
	"fmt"
	"log"

	"libvirt.org/go/libvirt"
)

func CreateVM() {
	const domainXML = `
	<domain type='kvm'>
	<name>golibvirt-vm</name>
	<memory unit='MiB'>1024</memory>
	<vcpu>1</vcpu>
	<os>
		<type arch='x86_64'>hvm</type>
		<boot dev='hd'/>
	</os>
	<devices>
		<disk type='file' device='disk'>
		<driver name='qemu' type='qcow2'/>
		<source file='/var/lib/libvirt/images/ubuntu.qcow2'/>
		<target dev='vda' bus='virtio'/>
		</disk>
		<interface type='network'>
		<source network='default'/>
		<model type='virtio'/>
		</interface>
		<graphics type='vnc' port='-1'/>
	</devices>
	</domain>`
	// 1) libvirt コネクションを開く
	conn, err := libvirt.NewConnect("qemu:///system")
	if err != nil {
		log.Fatalf("libvirt 接続失敗: %v", err)
	}
	defer conn.Close()

	// 2) ドメインを定義（XML を登録）
	dom, err := conn.DomainDefineXML(domainXML)
	if err != nil {
		log.Fatalf("ドメイン定義失敗: %v", err)
	}
	defer dom.Free() // 終了時にリソース解放

	// 3) ドメインを起動
	if err := dom.Create(); err != nil {
		log.Fatalf("ドメイン起動失敗: %v", err)
	}
	fmt.Println("VM を起動しました: golibvirt-vm")

	// 4) 状態確認（RUNNING なら 1）
	state, _, err := dom.GetState()
	if err != nil {
		log.Fatalf("ドメイン状態取得失敗: %v", err)
	}
	fmt.Printf("現在の状態: %d\n", state)
}
