#!/usr/bin/env python3
# import httpx
# import datetime
import sys
# from tabulate import tabulate

# from common import BASE_URL, HEADERS, print_resp, wait_tasks, Color


args = sys.argv


if __name__ == "__main__":
    if int(args[1]) == 1 and len(args) == 3:
        print("show delete post")
    
    if int(args[1]) == 1 and len(args) == 4:
        print("dele")
    
    if int(args[1]) == 2:
        print("vm task storage")
    
    f = open('./tests/compreply_debug.txt', 'w')
    f.write(str(args))
    f.close()