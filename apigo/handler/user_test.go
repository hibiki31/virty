package handler

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"virtygo/database"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
)

func TestCreateUser(t *testing.T) {
	userJSON := `{"Name":"Jon Snow","Email":"jon@labstack.com"}`

	// Setup
	e := echo.New()

	req := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(userJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	database.Connect()
	db, _ := database.DB.DB()
	defer db.Close()

	// Assertions
	if assert.NoError(t, CreateUser(c)) {
		assert.Equal(t, http.StatusCreated, rec.Code)
		// user := model.User{}
		// if err := c.Bind(&user); err != nil {
		// }
		// assert.Equal(t, "Jon Snow", user.Name)
	}
}
