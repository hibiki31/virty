package vxlan

import (
	"fmt"
	"net/http"
	"os/exec"
	"strconv"

	"virtyagent/model"

	"github.com/labstack/echo/v4"
)

func GetIndex(c echo.Context) error {
	rows := []model.VxlanConnectionModel{}
	model.DB.Find(&rows)
	return c.JSON(http.StatusOK, rows)
}

func PostVxlan(c echo.Context) error {
	request := new(model.VxlanConnectionModel)
	if err := c.Bind(&request); err != nil {
		return c.String(http.StatusBadRequest, "Error!")
	}
	model.DB.Create(&request)

	CreateVXLAN(request)

	msg := fmt.Sprintf("id: %v, name %v", request.VNI, request.RemoteIP)
	return c.String(http.StatusOK, string(msg))
}

func CreateVXLAN(m *model.VxlanConnectionModel) {
	fmt.Println(m)
	out, err := exec.Command("ip", "link", "add", "vx-"+m.NetworkID, "type", "vxlan", "id", strconv.Itoa(m.VNI), "remote", m.RemoteIP, "dstport", "4789").CombinedOutput()
	fmt.Printf("out:\n%s\nerror:\n%v\n", out, err)
	out, err = exec.Command("ip", "link", "set", "vx-"+m.NetworkID, "master", "vbr-"+m.NetworkID).CombinedOutput()
	fmt.Printf("out:\n%s\nerror:\n%v\n", out, err)
	out, err = exec.Command("ip", "link", "set", "vx-"+m.NetworkID, "up").CombinedOutput()
	fmt.Printf("out:\n%s\nerror:\n%v\n", out, err)
}

func Setup() {
	rows := []model.VxlanConnectionModel{}
	model.DB.Find(&rows)
	for _, s := range rows {
		CreateVXLAN(&s)
	}
}
