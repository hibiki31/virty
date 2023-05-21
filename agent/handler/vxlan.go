package handler

import (
	"net/http"
	"os/exec"
	"fmt"
	"strconv"

	"github.com/labstack/echo/v4"
	"virtyagent/model"
)

func PostVxlan(c echo.Context) error {
	request := new(model.PostVxlanReq)
	if err := c.Bind(&request); err != nil {
		return c.String(http.StatusBadRequest, "Error!")
	}
	model.DB.Create(&request)

	CreateVXLAN(request)

	msg := fmt.Sprintf("id: %v, name %v", request.VNI, request.RemoteIP)
	return c.String(http.StatusOK, string(msg))
}

func CreateVXLAN(m *model.PostVxlanReq) {
	out, err := exec.Command("ip", "link", "add", "vx-"+m.NetworkID, "type", "vxlan", "id", strconv.Itoa(m.VNI), "remote",m.RemoteIP, "dstport", "4789").CombinedOutput()
	fmt.Printf("out:\n%s\nerror:\n%v\n", out, err)
	out, err = exec.Command("ip", "link", "set", "vx-"+m.NetworkID, "master", "vbr-"+m.NetworkID).CombinedOutput()
	fmt.Printf("out:\n%s\nerror:\n%v\n", out, err)
	out, err = exec.Command("ip", "link", "set", "vx-"+m.NetworkID, "up").CombinedOutput()
	fmt.Printf("out:\n%s\nerror:\n%v\n", out, err)
}

func Setup() {
	rows := []model.PostVxlanReq{}
	model.DB.Find(&rows)
	for _, s := range rows {
		CreateVXLAN(&s)
	}
}