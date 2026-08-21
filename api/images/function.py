import re

import httpx


def url_body_size(
    url: str,
    foce_range: bool = False,
    *,
    follow_redirects: bool = True,
    use_proxy: bool = True,
) -> int | None:
    with httpx.Client(
        follow_redirects=follow_redirects,
        timeout=5,
        trust_env=use_proxy,
    ) as client:
        # HEADで確認
        if not foce_range:
            r = client.head(url)

            size = r.headers.get("Content-Length")
            if size is not None:
                return int(size)

        # Content-Rangeで確認
        headers = {"Range": "bytes=0-0"}
        r = client.get(url, headers=headers)
        r.raise_for_status()

    # Example: "bytes 0-0/12345678"
    m = re.match(r"bytes\s+\d+-\d+/(\d+)", r.headers.get("Content-Range", ""))
    if m:
        return int(m.group(1))
    
    return None
