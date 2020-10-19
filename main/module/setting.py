import os

script_path = os.getenv('VIRTY_PATH', '/opt/virty/app')
data_path = os.getenv('VIRTY_DATA', '/opt/virty/data')
web_secret = os.getenv('VIRTY_SECRET', 'secret-key')
database_path = data_path + '/data.sqlite'