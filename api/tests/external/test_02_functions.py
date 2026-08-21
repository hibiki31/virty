from images.function import url_body_size


def test_check_url(env):
    # 専用labが明示したdownload先以外へは接続しない。
    assert url_body_size(env.iso_url)
    assert url_body_size(env.image_url)

    assert url_body_size(env.iso_url, foce_range=True)
    assert url_body_size(env.image_url, foce_range=True)
