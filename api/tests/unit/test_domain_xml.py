import pytest

from module.xmllib import XmlEditor


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


def test_domain_parse_keeps_network_name_from_empty_source_element() -> None:
    domain = XmlEditor("static", "dom_ex_centos").domain_parse()

    assert len(domain.interface) == 1
    assert domain.interface[0].network == "ninon"
