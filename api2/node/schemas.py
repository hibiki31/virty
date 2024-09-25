                                                  lass Node(BaseSchema):
    name: str
    description: str
    domain: str
    user_name: str
    por   os_version: str
    status: int
    qemu_version: str | None = None
    libvirt_version: str | None = None
    roles: List[NodeRole]