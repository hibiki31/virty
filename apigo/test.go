package main

import (
	"fmt"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type User struct {
	gorm.Model
	Name  string
	Email string
}

func Test() {
	fmt.Print("hello")

	dsn := "host=db user=virty password=virty-passworde dbname=virty port=5432 " +
		"sslmode=disable TimeZone=Asia/Tokyo"
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}
	db.AutoMigrate(&User{})
	fmt.Println("migrated")

	var count int64
	db.Model(&User{}).Count(&count)
	if count == 0 {
		db.Create(&User{Name: "user01", Email: "xxxxxx@xxx01.com"})
		db.Create(&User{Name: "user02", Email: "xxxxxx@xxx02.com"})
		db.Create(&User{Name: "user03", Email: "xxxxxx@xxx03.com"})
	}

	var user User
	db.Where(User{Name: "user02"}).First(&user)
	fmt.Println(user)
}
