package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
)

func NodePost() {
	find_url := "http://192.168.144.33:8019/api/v2/resource/node/find"
	hostname, err := os.Hostname()

	find_query := map[string]interface{}{
		"hostname": hostname,
	}
	json_query, err := json.Marshal(find_query)
	nodeResp, err := http.Post(find_url, "application/json", bytes.NewBuffer(json_query))
	if err != nil {
		panic(err)
	}

	nodebody, err := io.ReadAll(nodeResp.Body)
	if err != nil {
		panic(err)
	}
	var resjson []NodeGetData
	if err := json.Unmarshal([]byte(nodebody), &resjson); err != nil {
		log.Fatalf("JSON アンマーシャル失敗: %v", err)
	}

	if len(resjson) != 0 {
		return
	}

	url := "http://192.168.144.33:8019/api/v2/resource/node"

	// 送信データ構造体
	payload := GetNodeInfo()
	jsonData, err := json.Marshal(payload)
	if err != nil {
		panic(err)
	}

	// POST送信
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}

	fmt.Println("ステータスコード:", resp.StatusCode)
	fmt.Println("レスポンスボディ:", string(body))
}
