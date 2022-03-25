#!/usr/bin/env python3
import os, glob
from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec = dict(
            path=dict(type='str', required=True)
        ),
    )
    path = module.params['path']

    data = list(glob.glob(f'{path}**'))
 
    module.exit_json(changed=False, data=data)

if __name__ == '__main__':
    main()