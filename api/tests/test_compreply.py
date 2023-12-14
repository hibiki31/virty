#!/usr/bin/env python3
# import httpx
# import datetime
import sys, re
# from tabulate import tabulate

# from common import BASE_URL, HEADERS, print_resp, wait_tasks, Color


def main():
    args = sys.argv
    
    f = open('./tests/compreply_debug.txt', 'w')
    f.write(str(args))
    f.close()
    
    args_1 = [
            "get", 
            "delete", 
            "create",
            "describe"
        ]
    
    if int(args[1]) == 1:
        print_comp(args_1, list_get(args, 3))
    
    elif int(args[1]) == 2 and args[3] == "get":
        print_comp(["task", "user", "vm", "node"], list_get(args, 4))


def print_comp(comp_list: list, query=None):
    if query:
        comp_list = [i for i in comp_list if query in i ]
    print(" ".join(comp_list))


def list_get(data, index):
    return data[index] if len(data) > index else None


if __name__ == "__main__":
    main()
