from virty import Client
from virty.api.auth import setup

clinet = Client(base_url="https://virty-dev.hinagiku.me")

data = setup.sync(client=clinet,json_body={"auth":"auth"})
print(data)