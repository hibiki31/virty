package main

import (
	// "context"
	// "fmt"
	"vctl/openapi"
	"vctl/cmd"
)


func main() {
	// cfg := openapi.NewConfiguration()
    // c := openapi.NewAPIClient(cfg)

	// ctx := context.Background()
    // pets, _, err := c.DefaultApi.PetsIdGet(ctx, 1)
    // pets, _, err := c.

    // fmt.Println(pets, err)

	cmd.Execute()
}
