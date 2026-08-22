from images.function import url_body_size


def test_check_url(env):
    # 専用labが明示したdownload先以外へは接続しない。
    for url in (env.iso_url, env.image_url):
        head_size = url_body_size(url)
        range_size = url_body_size(url, foce_range=True)
        assert isinstance(head_size, int)
        assert head_size > 0
        assert range_size == head_size
