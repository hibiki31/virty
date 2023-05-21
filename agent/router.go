package main

import (
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	
	"virtyagent/handler"
	"virtyagent/model"
)

func main() {
	e := echo.New()

	e.Use(middleware.Logger())
	// e.Use(middleware.Recover())

	e.GET("/", getIndex)
	e.POST("/vxlan", handler.PostVxlan)

	model.Init()
	handler.Setup()

	e.Logger.Fatal(e.Start(":8766"))
}


func getIndex(c echo.Context) error {
	return c.String(http.StatusOK, "Running virty Aget !!!")
}