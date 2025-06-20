package model

type VxlanConnectionModel struct {
	VNI int `gorm:"primaryKey;autoIncrement:false" json:"vni"`
	// NetworkIDはVNIを16進数に変換したもの
	NetworkID string `json:"networkID"`
	NodeID    string `json:"nodeID"`
	RemoteIP  string `json:"remoteIP"`
}
