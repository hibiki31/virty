import httpx

# Cloudflare APIのエンドポイントと認証情報
CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4"
API_TOKEN = ""
ZONE_ID = "" #ダッシュボードから取得

# ヘッダーの設定
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def create_dns_record(record_type, name, content, ttl=180, proxied=False):
    url = f"{CLOUDFLARE_API_URL}/zones/{ZONE_ID}/dns_records"
    payload = {
        "type": record_type,
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied
    }
    response = httpx.post(url, headers=headers, json=payload)
    return response.json()

def delete_dns_record(record_id):
    url = f"{CLOUDFLARE_API_URL}/zones/{ZONE_ID}/dns_records/{record_id}"
    response = httpx.delete(url, headers=headers)
    return response.json()

def update_dns_record(record_id, record_type, name, content, ttl=120, proxied=False):
    url = f"{CLOUDFLARE_API_URL}/zones/{ZONE_ID}/dns_records/{record_id}"
    payload = {
        "type": record_type,
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied
    }
    response = httpx.put(url, headers=headers, json=payload)
    return response.json()

# DNSレコードの作成例
create_response = create_dns_record("A", "example.com", "192.0.2.1")
print("Create Response:", create_response)

# 作成したDNSレコードのIDを取得（例として）
# record_id = create_response.get("result", {}).get("id")

# DNSレコードの更新例
# if record_id:
#     update_response = update_dns_record(record_id, "A", "example.com", "192.0.2.2")
#     print("Update Response:", update_response)

# DNSレコードの削除例
# if record_id:
#     delete_response = delete_dns_record(record_id)
#     print("Delete Response:", delete_response)
def list_dns_records():
    url = f"{CLOUDFLARE_API_URL}/zones/{ZONE_ID}/dns_records"
    response = httpx.get(url, headers=headers)
    return response.json()

print(list_dns_records())