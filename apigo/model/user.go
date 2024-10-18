package model

type UserCreate struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

type User struct {
	Model
	Name  string `json:"name"`
	Email string `json:"email"`
}
