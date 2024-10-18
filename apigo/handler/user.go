package handler

import (
	"net/http"

	"virtygo/database"
	"virtygo/model"

	"gorm.io/gorm"

	"github.com/labstack/echo/v4"
)

func MountUser(e *echo.Echo) {
	e.GET("/users", GetUsers)
	e.GET("/users/:id", GetUser)
	e.PUT("/users/:id", UpdateUser)
	e.POST("/users", CreateUser)
	e.DELETE("/users/:id", DeleteUser)
}

// GetUser godoc
//
//	@Produce	json
//	@Success	200	{object}	model.UserCreate
//	@Router		/users [GET]
func GetUsers(c echo.Context) error {
	users := []model.User{}
	database.DB.Find(&users)
	return c.JSON(http.StatusOK, users)
}

// GetUser godoc
//
//	@Produce	json
//	@Param		id	path		int	false	"ID"
//	@Success	200	{object}	model.User
//	@Router		/users/{id} [get]
func GetUser(c echo.Context) error {
	user := model.User{}
	id := c.Param("id")

	result := database.DB.First(&user, id)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			// レコードが見つからなかった場合、404を返す
			return c.NoContent(http.StatusNotFound)
		}
		// 他のエラーが発生した場合、500を返す
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"message": "Something went wrong",
		})
	}

	return c.JSON(http.StatusOK, user)
}

// UpdateUser godoc
//
//	@Produce	json
//	@Param		id		path		int					false	"ID"
//	@Param		body	body		model.UserCreate	false	"Body"
//	@Success	200		{object}	model.User
//	@Router		/users/{id} [put]
func UpdateUser(c echo.Context) error {
	user := model.User{}
	id := c.Param("id")

	if err := database.DB.First(&user, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return c.NoContent(http.StatusNotFound)
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"message": "Internal server error",
		})
	}

	if err := c.Bind(&user); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"message": "Invalid request data",
		})
	}

	// 全フィールドを更新
	if err := database.DB.Save(&user).Error; err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"message": "Error updating user",
		})
	}
	return c.JSON(http.StatusOK, user)
}

// CreateUser godoc
//
//	@Accept		json
//	@Produce	json
//	@Param		body	body		model.UserCreate	false	"aaaa"
//	@Success	200		{object}	model.User
//	@Router		/users [post]
func CreateUser(c echo.Context) error {
	user := model.User{}
	if err := c.Bind(&user); err != nil {
		return err
	}
	database.DB.Create(&user)
	return c.JSON(http.StatusCreated, user)
}

// DeleteUser godoc
//
//	@Accept		json
//	@Security	ApiKeyAuth
//	@Param		id	path	int	false	"ID"
//	@Success	204
//	@Router		/users/{id} [delete]
func DeleteUser(c echo.Context) error {
	id := c.Param("id")
	database.DB.Delete(&model.User{}, id)
	return c.NoContent(http.StatusNoContent)
}
