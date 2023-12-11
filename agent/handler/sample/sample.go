package sample

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

func GetIndex(c echo.Context) error {
	return c.String(http.StatusOK, "Hello World")
}

func GetUser(c echo.Context) error {
	id := c.Param("id")
	return c.String(http.StatusOK, id)
}

func GetUserQuery(c echo.Context) error {
	team := c.QueryParam("team")
	member := c.QueryParam("member")
	return c.String(http.StatusOK, "team:"+team+", member:"+member)
}

type User struct {
	Name  string `json:"name" xml:"name" form:"name" query:"name"`
	Email string `json:"email" xml:"email" form:"email" query:"email"`
}

func PostUser(c echo.Context) error {
	u := new(User)
	if err := c.Bind(u); err != nil {
		return err
	}
	return c.JSON(http.StatusCreated, u)
	// or
	// return c.XML(http.StatusCreated, u)
}
