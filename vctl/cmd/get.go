/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"context"
	"fmt"

	"github.com/spf13/cobra"
)

// getCmd represents the get command
var getCmd = &cobra.Command{
	Use:   "get",
	Short: "show subcommand",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("get called")
	},
}

var getNodeCmd = &cobra.Command{
	Use:   "node",
	Short: "get nodes list",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		c := GetClient()
		ctx := context.TODO()
		res, _, _ := c.NodesAPI.GetNode(ctx, "").Execute()

		for _, i := range res.Data {
			fmt.Println(i.Name, i.Domain, i.OsName, i.CpuGen, i.Memory)
		}
	},
}

var getVMCmd = &cobra.Command{
	Use:   "vm",
	Short: "get vms list",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		c := GetClient()
		ctx := context.TODO()
		r := c.VmsAPI.GetVms(ctx).Limit(15).Page(0)
		res, _, _ := r.Execute()

		for _, i := range res.Data {
			fmt.Println(i.Name, i.Uuid, i.Core, i.Memory, i.NodeName)
		}
	},
}

var getTaskCmd = &cobra.Command{
	Use:   "task",
	Short: "get tasks list",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		c := GetClient()
		ctx := context.TODO()
		r := c.TasksAPI.GetTasks(ctx).Limit(10)
		res, _, _ := r.Execute()

		for _, i := range res.Data {
			fmt.Println(i.PostTime, *i.Uuid, *i.Method, *i.Object, *i.Resource, *i.Message)
		}
	},
}

func init() {
	getCmd.AddCommand(getNodeCmd)
	getCmd.AddCommand(getVMCmd)
	getCmd.AddCommand(getTaskCmd)

	rootCmd.AddCommand(getCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// getCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// getCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
