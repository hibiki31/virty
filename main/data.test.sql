select img.name,img.node,img.pool,img.capa,img.allocation,img.physical,img.path,domain.name,count(*),archive_img.archive_id from img left join domain_drive on img.path=domain_drive.source  left join domain  on domain_drive.dom_uuid=domain.uuid and img.node=domain.node_name left join archive_img on img.name=archive_img.name group by img.node,img.path;

