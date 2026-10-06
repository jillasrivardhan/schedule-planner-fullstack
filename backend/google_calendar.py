from datetime import datetime, timedelta
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from .config import GOOGLE_CLIENT_SECRETS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_REDIRECT_URI, SCOPES


def is_connected() -> bool:
    return GOOGLE_TOKEN_FILE.exists()


def _load_credentials() -> Optional[Credentials]:
    if not GOOGLE_TOKEN_FILE.exists():
        return None
    return Credentials.from_authorized_user_file(str(GOOGLE_TOKEN_FILE), SCOPES)


def create_auth_flow():
    if not GOOGLE_CLIENT_SECRETS_FILE.exists():
        raise FileNotFoundError("credentials.json was not found. Put your Google OAuth client JSON in the project root.")
    return Flow.from_client_secrets_file(
        str(GOOGLE_CLIENT_SECRETS_FILE), scopes=SCOPES, redirect_uri=GOOGLE_REDIRECT_URI
    )


def get_authorization_url():
    flow = create_auth_flow()
    url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    return url, state


def complete_authorization(code: str):
    flow = create_auth_flow()
    flow.fetch_token(code=code)
    GOOGLE_TOKEN_FILE.write_text(flow.credentials.to_json(), encoding="utf-8")


def get_service():
    credentials = _load_credentials()
    if not credentials or not credentials.valid:
        return None
    return build("calendar", "v3", credentials=credentials)


def get_events(target_date: str):
    service = get_service()
    if service is None:
        return []
    start = datetime.fromisoformat(f"{target_date}T00:00:00+05:30")
    end = start + timedelta(days=1)
    response = service.events().list(
        calendarId="primary", timeMin=start.isoformat(), timeMax=end.isoformat(),
        singleEvents=True, orderBy="startTime"
    ).execute()
    events = []
    for event in response.get("items", []):
        start_value = event.get("start", {}).get("dateTime")
        end_value = event.get("end", {}).get("dateTime")
        if not start_value or not end_value:
            continue
        start_dt = datetime.fromisoformat(start_value.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_value.replace("Z", "+00:00"))
        events.append({
            "id": event.get("id"), "title": event.get("summary", "Untitled event"),
            "date": target_date, "start_time": start_dt.strftime("%H:%M"),
            "end_time": end_dt.strftime("%H:%M"), "description": event.get("description", ""),
            "source": "google"
        })
    return events


def create_event(target_date: str, start_time: str, end_time: str, title: str, description: str = ""):
    service = get_service()
    if service is None:
        raise RuntimeError("Google Calendar is not connected.")
    body = {
        "summary": title, "description": description,
        "start": {"dateTime": f"{target_date}T{start_time}:00+05:30", "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": f"{target_date}T{end_time}:00+05:30", "timeZone": "Asia/Kolkata"},
    }
    return service.events().insert(calendarId="primary", body=body).execute()
