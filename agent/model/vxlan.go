package model

type PostVxlanReq struct {
	VNI   int    `gorm:"primaryKey;autoIncrement:false" json:"vni"`
	NetworkID string `json:"networkId"`
	RemoteIP string `json:"remoteIP"`
}
