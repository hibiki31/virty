package main

import (
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	"virtyagent/handler/address"
	"virtyagent/handler/sample"
	"virtyagent/handler/vxlan"
	"virtyagent/model"
)

func main() {
	e := echo.New()

	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	e.GET("/sample", sample.GetIndex)
	e.GET("/sample/users/:id", sample.GetUser)
	e.GET("/sample/users", sample.GetUserQuery)
	e.POST("/sample/users", sample.PostUser)
	e.GET("/address", address.GetAddress)
	e.GET("/address/ip", address.GetAddressIP)

	e.POST("/vxlan", vxlan.PostVxlan)
	e.GET("/vxlan", vxlan.GetIndex)

	model.Init()
	vxlan.Setup()

	e.Logger.Fatal(e.Start(":8766"))
}
