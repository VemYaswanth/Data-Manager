from services.file_service_db import get_project_files_latest
from services.project_db import get_project_by_id


def build_project_file_tree(project_id: int):
    project = get_project_by_id(project_id)
    if not project:
        return None

    files = get_project_files_latest(project_id)

    tree = {
        "project_id": project_id,
        "project_name": project["name"],
        "files": []
    }

    for f in files:
        tree["files"].append({
            "file_id": f["id"],
            "name": f["name"],
            "version": f["version"],
            "latest": bool(f["is_latest"]),
            "size": f["size"],
            "modified": f["modified_at"]
        })

    return tree
