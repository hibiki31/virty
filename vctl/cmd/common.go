package cmd

import (
	"os"
	"path/filepath"

	openapi "github.com/hibiki31/virty-go"
	"gopkg.in/yaml.v2"
)

func GetClient() *openapi.APIClient {
	config := Configfile{}

	home_dir, _ := os.UserHomeDir()
	b, _ := os.ReadFile(filepath.Join(home_dir, ".virtyctl"))

	yaml.Unmarshal(b, &config)

	cfg := openapi.NewConfiguration()
	cfg.Servers = openapi.ServerConfigurations{
		{
			URL:         config.Endpoint,
			Description: "Default",
		},
	}
	cfg.AddDefaultHeader("Authorization", config.AccessToken)
	c := openapi.NewAPIClient(cfg)
	return c
}
