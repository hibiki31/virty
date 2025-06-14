
```
xml=$(< test.xml)
json=$(jq -n --arg xml "$xml" '{ xml: $xml }')

# 2) curl で POST
curl -X POST http://192.168.144.33:8019/api/v2/resource/vm.libvirt.virty \
  -H "Content-Type: application/json" \
  -d "$json"
```