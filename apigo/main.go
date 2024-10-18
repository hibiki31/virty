package main

import (
	"virtygo/database"
	"virtygo/handler"

	_ "virtygo/docs"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	echoSwagger "github.com/swaggo/echo-swagger"
)

// @title			Recommend Swaggo API
// @version		1.0
// @description	This is a recommend_swaggo server
// @license.name	Apache 2.0
// @license.url	http://www.apache.org/licenses/LICENSE-2.0.html
// @host			localhost:8765
// @in				header
func main() {

	e := echo.New()

	database.Connect()
	db, _ := database.DB.DB()
	defer db.Close()

	handler.MountUser(e)

	e.Use(middleware.CORS())
	e.GET("/api/*", echoSwagger.WrapHandler)

	e.Logger.Fatal(e.Start(":8765"))
}
