from typing import List

from sqlalchemy.orm import Session

from module.virtlib import VirtManager
from node.models import NodeModel
from storage.models import ImageModel, StorageModel


def storage_rescan(node: NodeModel, db:Session, token:str, storage_uuids:List[str]=[]):
    if node.status != 10:
        return [], []

    manager = VirtManager(node_model=node)

    if len(storage_uuids) == 0:
        storages = manager.storages_data(token=token)
        for storage in storages:
            storage_model = StorageModel(**storage.model_dump(exclude={"allocation", "images"}))
            for image in storage.images:
                image_model = ImageModel(**image.model_dump())
                db.merge(image_model)
            db.merge(storage_model)

        db.commit()
        # トークンで除外
        db.query(StorageModel).filter(
            StorageModel.update_token!=token, 
            StorageModel.node_name==node.name
            ).delete()
        db.query(ImageModel).filter(
            ImageModel.update_token != token,
            ImageModel.storage.has(StorageModel.node_name == node.name)
            ).delete(synchronize_session=False)
        db.commit()
    else:
        storages = manager.storages_data(token=token, uuids=storage_uuids)
        for storage in storages:
            storage_model = StorageModel(**storage.model_dump(exclude={"allocation", "images"}))
            for image in storage.images:
                image_model = ImageModel(**image.model_dump())
                db.merge(image_model)
            db.merge(storage_model)
            db.commit()
            # トークンで除外
            db.query(StorageModel).filter(
                StorageModel.update_token!=token, 
                StorageModel.node_name==node.name,
                StorageModel.uuid==storage.uuid
                ).delete()
            db.query(ImageModel).filter(
                ImageModel.update_token != token,
                ImageModel.storage.has(StorageModel.uuid == storage.uuid)
                ).delete(synchronize_session=False)
            db.commit()