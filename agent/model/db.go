package model

import (
	"github.com/caarlos0/env/v10"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var DB *gorm.DB
var err error

type DBConfig struct {
	VIRTY_AGENT_DBPATH string `env:"VIRTY_AGENT_DBPATH" envDefault:"/opt/virty/agent.sqlite"`
}

func Init() {
	cfg := DBConfig{}
	env.Parse(&cfg)

	DB, err = gorm.Open(sqlite.Open(cfg.VIRTY_AGENT_DBPATH), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}
	DB.AutoMigrate(&VxlanConnectionModel{})
}
