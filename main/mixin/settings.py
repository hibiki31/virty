import os


virty_root = os.getenv('VIRTY_ROOT', './')
is_dev = False

if virty_root == './':
    is_dev = True