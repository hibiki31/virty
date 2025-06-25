from storage.schemas import ImageForXML, StorageForXML

from .base import XmlEditor
from .utils import unit_convertor


class StorageXmlEditor(XmlEditor):
    def storage_pase(self) -> StorageForXML:
        if target := self.xml.find('target'):
            target_path = target.find('path').text
        else:
            target_path = None
        
        res = StorageForXML(
            name = self.xml.find('name').text,
            uuid = self.xml.find('uuid').text,
            capacity = unit_convertor(self.xml.find('capacity').get("unit"), "G", self.xml.find('capacity').text),
            available = unit_convertor(self.xml.find('available').get("unit"), "G",  self.xml.find('available').text),
            allocation = unit_convertor(self.xml.find('allocation').get("unit"), "G", self.xml.find('allocation').text),
            path=target_path
        )
        return res
    
    def image_pase(self):
        res = ImageForXML(
            name = self.xml.find('name').text,
            capacity = int(unit_convertor( self.xml.find('capacity').get("unit"), "G",  self.xml.find('capacity').text)),
            allocation = int(unit_convertor( self.xml.find('allocation').get("unit"), "G",  self.xml.find('allocation').text)),
            path = self.xml.find('target').find('path').text
        )

        return res