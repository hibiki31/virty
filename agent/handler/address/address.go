package address

import (
	"encoding/json"
	"net/http"
	"os/exec"

	"github.com/labstack/echo/v4"
)

func GetAddress(c echo.Context) error {
	res := cmdAddress()
	return c.JSONBlob(http.StatusOK, res)
	// return c.JSON(http.StatusCreated, res)
}

func GetAddressIP(c echo.Context) error {
	var data Address
	json.Unmarshal(cmdAddress(), &data)

	var res []AddressIP

	for _, v := range data {
		for _, f := range v.AddrInfo {
			res = append(res, AddressIP{Local: f.Local})
		}
	}

	return c.JSON(http.StatusOK, res)
}

func cmdAddress() []byte {
	out, _ := exec.Command("ip", "-json", "address").CombinedOutput()
	return out
}
