#!/usr/bin/env python3
import os
from ansible.module_utils.basic import AnsibleModule

def test():
    play_source = dict(
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(
                qemu_img = dict(
                    dest = "/tmp/test.img",
                    size = "32G",
                    state = "present"
                ),
                become = "yes"
            )
        ]
    )

def main():
    module = AnsibleModule(
        argument_spec = dict(
            dest=dict(type='str', required=True),
            format=dict(type='str', default='qcow2'),
            size=dict(type='str'),
            state=dict(type='str', choices=['absent', 'present', 'resize'], default='present'),
        ),
    )

    changed = False

    img_dst = module.params['dest']
    img_format = module.params['format']
    img_size = module.params['size']
    qemu_img_cmd = module.get_bin_path('qemu-img', True)
    become_status = module.params['state']
    
    if img_size != None:
        if(img_size[:-1].upper == 'G'):
            img_size = img_size[:-1] * 1024 * 1024 * 1024
        elif(img_size[:-1].upper == 'M'):
            img_size = img_size[:-1] * 1024 * 1024
        elif(img_size[:-1].upper == 'K'):
            img_size = img_size[:-1] * 1024
        else:
            img_size = img_size

    if become_status == 'present':
        if not img_size:
            module.fail_json(msg='Requires a image size')
        if not os.path.exists(img_dst):
            module.run_command(f'{qemu_img_cmd} create -f {img_format} "{img_dst}" {img_size}', check_rc=True)
            changed = True

    if become_status == 'resize':
        if not size:
            module.fail_json(msg='Requires a image size')            
        if not os.path.exists(img_dst):
            module.fail_json(msg='Terget file not found')
        else:
            module.run_command('%s resize "%s" %s'%(qemu_img, dest, size), check_rc=True)
            changed = True

    if become_status == 'absent':
        if os.path.exists(img_dst):
            os.remove(img_dst)
            changed = True

    module.exit_json(changed=changed)

main()