package main

import (
	"fmt"
	"log"
	"os"

	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/host"
	"github.com/shirou/gopsutil/v3/mem"
)

func GetNodeInfo() NodePostData {
	hostname, err := os.Hostname()
	if err != nil {
		// エラー時の処理
		fmt.Fprintf(os.Stderr, "ホスト名の取得に失敗: %v\n", err)
		os.Exit(1)
	}

	// --- メモリ取得 ---
	vm, err := mem.VirtualMemory()
	if err != nil {
		log.Fatalf("メモリ情報取得エラー: %v", err)
	}
	// バイト→GiB換算
	totalGB := float64(vm.Total) / (1024 * 1024 * 1024)
	fmt.Printf("総メモリ量: %.2f GB\n", totalGB)

	// --- CPU 型番＋コア数取得 ---
	infos, err := cpu.Info()
	if err != nil || len(infos) == 0 {
		log.Fatalf("CPU情報取得エラー: %v", err)
	}
	// CPU モデル名（複数ソケットある場合は infos[0] を代表として）
	model := infos[0].ModelName

	// 論理コア数（ハイパースレッド含む）
	logicalCores, err := cpu.Counts(true)
	if err != nil {
		log.Fatalf("CPUコア数取得エラー: %v", err)
	}
	fmt.Printf("CPU 型番: %s\n", model)
	fmt.Printf("論理コア数: %d\n", logicalCores)

	// --- OS 名取得 ---
	hi, err := host.Info()
	if err != nil {
		log.Fatalf("ホスト情報取得エラー: %v", err)
	}
	fmt.Printf("OS: %s %s (%s)\n", hi.Platform, hi.PlatformVersion, hi.OS)

	payload := NodePostData{
		Hostname: hostname,
		Core:     logicalCores,
		Model:    model,
		Memory:   totalGB,
		Os:       hi.Platform,
	}
	return payload
}
