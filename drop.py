import dropbox
import os
from access import API
from dropbox.exceptions import ApiError

def sync_archive_to_dropbox(local_folder="/home/admin/archives"):
    """
    Uploads files from local 'archive' folder to Dropbox root if they do not exist.

    :param access_token: Dropbox API access token.
    :param local_folder: Local folder path (default: "archive").
    """
    
    if not os.path.exists(local_folder):
        print(f"⚠️ Local folder '{local_folder}' does not exist. Nothing to upload.")
        return

    dbx = dropbox.Dropbox(API)

    for file_name in os.listdir(local_folder):
        local_path = os.path.join(local_folder, file_name)
        dropbox_path = "/" + file_name  # root-level file in Dropbox

        if os.path.isfile(local_path):
            try:
                # Check if file exists in Dropbox root
                dbx.files_get_metadata(dropbox_path)
                print(f"✅ Skipping (already exists): {file_name}")
            except ApiError:
                # Not found → upload
                with open(local_path, "rb") as f:
                    dbx.files_upload(f.read(), dropbox_path)
                print(f"⬆️ Uploaded: {file_name}")
