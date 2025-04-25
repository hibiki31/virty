import json

from module import ansiblelib_test
from tests.model import TestEnviroment


def main():
    env = TestEnviroment(**json.load(open('./tests/env.json', 'r')))
    
    ansiblelib_test.main(env=env)

if __name__ == "__main__":
    main()