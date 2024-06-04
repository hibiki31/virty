from enum import Enum


class NetworkForCreateType(str, Enum):
    BRIDGE = "bridge"
    OVS = "ovs"

    def __str__(self) -> str:
        return str(self.value)
