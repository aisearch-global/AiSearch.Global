"""
Run this script ONCE locally to obtain a long-lived OAuth refresh token.
The token is printed to stdout — copy it into your GitHub repo secret GCP_REFRESH_TOKEN.

Usage:
    pip install google-auth-oauthlib
    python get_refresh_token.py
"""

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_ID = "YOUR_CLIENT_ID"       # Replace with your GCP OAuth Client ID
CLIENT_SECRET = "YOUR_CLIENT_SECRET"  # Replace with your GCP OAuth Client Secret

CLIENT_CONFIG = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

SCOPES = ["https://www.googleapis.com/auth/blogger"]


def main():
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0)
    print("\n--- COPY THE REFRESH TOKEN BELOW ---")
    print(creds.refresh_token)
    print("------------------------------------\n")
    print("Add it to GitHub → Settings → Secrets → GCP_REFRESH_TOKEN")


if __name__ == "__main__":
    main()
