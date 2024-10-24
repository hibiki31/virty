package handler

import (
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
)

func MountToken(e *echo.Echo) {
	e.POST("/token", CreateToken)
}

func generate() (string, error) {
	secret := []byte("test")

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.RegisteredClaims{
		Issuer:    "issuer",
		Subject:   "subject",
		Audience:  []string{"audience"},
		ExpiresAt: jwt.NewNumericDate(time.Now().Add(10 + time.Minute)),
		NotBefore: jwt.NewNumericDate(time.Now()),
		IssuedAt:  jwt.NewNumericDate(time.Now()),
		ID:        "id",
	})
	tokenString, err := token.SignedString(secret)
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

// CreateToken godoc
//
//	@Accept		json
//	@Security	ApiKeyAuth
//	@Success	201
//	@Router		/token [post]
func CreateToken(c echo.Context) error {
	token, err := generate()
	if err != nil {
		return c.JSON(http.StatusBadRequest, err)
	}

	return c.JSON(http.StatusCreated, token)
}
