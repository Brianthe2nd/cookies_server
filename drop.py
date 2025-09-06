import os
import dropbox
from dropbox.exceptions import ApiError, AuthError

# Move these to a secure place (env vars or config file)
APP_KEY = "bor1biqle1g1xn3"
APP_SECRET = "lco6yv2zqa8c3kr"
REFRESH_TOKEN = "V3C64ZrOgugAAAAAAAAAGi08Y2YTB74bu0shwF-QvTY"  # you got this after OAuth flow

def sync_archive_to_dropbox(local_folder="/home/admin/archives"):
    """
    Uploads files from local 'archive' folder to Dropbox root if they do not exist.
    Automatically refreshes tokens via Dropbox SDK.
    """
    if not os.path.exists(local_folder):
        print(f"⚠️ Local folder '{local_folder}' does not exist. Nothing to upload.")
        return

    try:
        # SDK handles refreshing access tokens internally
        dbx = dropbox.Dropbox(
            app_key=APP_KEY,
            app_secret=APP_SECRET,
            oauth2_refresh_token=REFRESH_TOKEN
        )
        dbx.users_get_current_account()
    except AuthError:
        print("❌ Authentication failed. Check APP_KEY, APP_SECRET, or REFRESH_TOKEN.")
        return

    for file_name in os.listdir(local_folder):
        local_path = os.path.join(local_folder, file_name)
        dropbox_path = "/" + file_name

        if os.path.isfile(local_path):
            try:
                dbx.files_get_metadata(dropbox_path)
                print(f"✅ Skipping (already exists): {file_name}")
            except ApiError:
                # Not found → upload
                with open(local_path, "rb") as f:
                    dbx.files_upload(
                        f.read(),
                        dropbox_path
                    )
                print(f"⬆️ Uploaded: {file_name}")


# if __name__ == "__main__":
#     sync_archive_to_dropbox()