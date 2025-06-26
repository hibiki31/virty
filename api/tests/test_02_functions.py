from images.function import url_body_size


def test_check_url(env):
    assert url_body_size("https://www.google.com/") is None
    assert url_body_size("https://www.google.com/", foce_range=True) is None
    
    assert url_body_size(env.iso_url)
    assert url_body_size(env.image_url)
    
    assert url_body_size(env.iso_url, foce_range=True)
    assert url_body_size(env.image_url, foce_range=True)