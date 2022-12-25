/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"
	"log"
	"os"
	"io/ioutil"
	"net/http"
	"net/url"
	"github.com/spf13/cobra"
	"github.com/go-yaml/yaml"
	"encoding/json"
	"path/filepath"
	"strconv"
)

var apiURL string

type Response struct {
	AccessToken string `json:"access_token"`
}

type Configfile struct {
	AccessToken string
	Endpoint string
}

// loginCmd represents the login command
var loginCmd = &cobra.Command{
	Use:   "login",
	Short: "A brief description of your command",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		var username, password string
		fmt.Print("username: ")
		fmt.Scan(&username)
		fmt.Print("password: ")
		fmt.Scan(&password)

		postData := url.Values{}
		postData.Add("username", username)
		postData.Add("password", password)

		resp, err := http.PostForm(apiURL + "/api/auth", postData)
        if err != nil {
            log.Fatal(err)
        }
		
		defer resp.Body.Close()

		if resp.StatusCode >= 400 {
			fmt.Println(fmt.Errorf("bad response status code %d", resp.StatusCode))
			return
		}

		var response Response


		body, _ := ioutil.ReadAll(resp.Body)
		
		if err := json.Unmarshal(body, &response); err != nil {
			fmt.Println(err)
			return
		}
		fmt.Printf("Successfully logged in.\nConfiguration file is tored in ~/.virtyctl\n")

		var configfile Configfile

		configfile.AccessToken = "Bearer " + response.AccessToken
		configfile.Endpoint = apiURL

		buf, _ := yaml.Marshal(configfile)                          
                                   
		// []byte をファイルに上書きしています。 
		conf, err := os.UserHomeDir()
		perm := "0600"
		perm32, _ := strconv.ParseUint(perm, 8, 32)
		err = ioutil.WriteFile(filepath.Join(conf, ".virtyctl"), buf, os.FileMode(perm32)) 
		os.Chmod(filepath.Join(conf, ".virtyctl"), 0600)          
	},
}

func init() {
	rootCmd.AddCommand(loginCmd)

	loginCmd.Flags().StringVarP(&apiURL, "api", "", "", "Ex. https://192.168.1.1/api")
	loginCmd.MarkFlagRequired("api")
	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// loginCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// loginCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
