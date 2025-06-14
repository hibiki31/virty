package main

type NodePostData struct {
	Core     int     `json:"core"`
	Hostname string  `json:"hostname"`
	Memory   float64 `json:"memory"`
	Model    string  `json:"model"`
	Os       string  `json:"os"`
	UserID   int     `json:"userId,omitempty"`
}

type NodeGetData struct {
	ID       string  `json:"_id,omitempty"`
	Core     int     `json:"core"`
	Hostname string  `json:"hostname"`
	Memory   float64 `json:"memory"`
	Model    string  `json:"model"`
	Os       string  `json:"os"`
}
