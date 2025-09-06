import requests

APP_KEY = "bor1biqle1g1xn3"
APP_SECRET = "lco6yv2zqa8c3kr"

# Dropbox OAuth 2.0 authorize URL (asks Dropbox for offline access = refresh token)
auth_url = (
    f"https://www.dropbox.com/oauth2/authorize"
    f"?client_id={APP_KEY}"
    f"&token_access_type=offline"
    f"&response_type=code"
)

print("👉 Open this URL in a browser and approve access:")
print(auth_url)

# You’ll get a ?code=XXXX at the end → paste it here
auth_code = input("Paste the authorization code here: ")

# Exchange auth code for refresh token
resp = requests.post(
    "https://api.dropboxapi.com/oauth2/token",
    data={
        "code": auth_code,
        "grant_type": "authorization_code",
    },
    auth=(APP_KEY, APP_SECRET),
)

if resp.status_code != 200:
    print("❌ Error getting token:", resp.text)
    exit()

tokens = resp.json()
print("✅ Got tokens:")
print(tokens)

REFRESH_TOKEN = tokens["refresh_token"]
print("🔑 Save this refresh token securely:", REFRESH_TOKEN)
