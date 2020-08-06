import os

scriptPath = os.getenv('VIRTY_PATH', '/root/virty/main')
webSecret = os.getenv('VIRTY_SECRET', 'secret-key')
databasePath = scriptPath + "/data.sqlite"