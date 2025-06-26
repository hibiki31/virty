import httpx

url = "https://download.rockylinux.org/pub/rocky/10/isos/x86_64/Rocky-10.0-x86_64-dvd1.iso"

r = httpx.head(url, follow_redirects=True, timeout=5)
r.raise_for_status()                     # 4xx/5xx を例外に
size = r.headers.get("Content-Length")   # 文字列（なければ None）
if size is not None:
    print(f"{int(size):,} bytes")
else:
    print("Content-Length が帰ってきませんでした")
