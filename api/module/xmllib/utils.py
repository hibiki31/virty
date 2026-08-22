import random
import xml.etree.ElementTree as ET


class UnitConvertFailed(Exception):
    pass


def unit_convertor(from_unit, to_unit, value) -> int:
    if from_unit == "bytes" and to_unit == "G":
        return int(float(value)/1024/1024/1024)
    elif from_unit == "bytes" and to_unit == "M":
        return int(float(value)/1024/1024)
    elif from_unit == "KiB" and to_unit == "M":
        return int(float(value)/1024)
    else:
        raise UnitConvertFailed(f"unknown convert pair {from_unit} => {to_unit}, {value}")


def macaddress_generator():
    
    mac = [ 0x00, 0x16, 0x3e,
    random.randint(0x00, 0x7f),
    random.randint(0x00, 0xff),
    random.randint(0x00, 0xff) ]
    return( ':'.join(map(lambda x: "%02x" % x, mac)))


def redact_domain_xml_secrets(xml_text: str) -> str:
    """libvirt domain XMLからconsole credentialを除去する。"""

    root = ET.fromstring(xml_text)
    changed = False
    for graphics in root.findall("./devices/graphics"):
        for attribute in ("passwd", "passwdValidTo"):
            if graphics.attrib.pop(attribute, None) is not None:
                changed = True
    return ET.tostring(root, encoding="unicode") if changed else xml_text
