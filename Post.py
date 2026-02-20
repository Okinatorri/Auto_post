import os
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

DELAY_BETWEEN_UPLOADS = 60000  # 16 часов (в секундах)
ACCOUNTS = ["account2"]



def upload_video(youtube, video_path):
    title = os.path.splitext(os.path.basename(video_path))[0]
    description = "#shorts"

    tags = [
        "shorts", "funny", "viral", "memes", "comedy",
        "entertainment", "trending", "youtube", "shortvideo",
        "lol", "humor", "daily", "reaction", "cute", "animals"
    ]

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    response = request.execute()
    return response["id"]


def run_account(account_name):
    print(f"\n===== Работаем с {account_name} =====")

    BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), account_name)
    SHORTS_DIR = os.path.join(BASE_DIR, "shorts")
    UPLOADED_DIR = os.path.join(BASE_DIR, "uploaded")
    TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
    CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")

    os.makedirs(SHORTS_DIR, exist_ok=True)
    os.makedirs(UPLOADED_DIR, exist_ok=True)

    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    youtube = build("youtube", "v3", credentials=creds)

    videos = sorted([f for f in os.listdir(SHORTS_DIR) if f.endswith(".mp4")])

    if not videos:
        print("Нет видео для загрузки.")
        return

    video = videos[0]
    video_path = os.path.join(SHORTS_DIR, video)

    print(f"Загружаю: {video}")

    try:
        video_id = upload_video(youtube, video_path)
        print(f"Успешно: https://youtube.com/watch?v={video_id}")

        os.rename(video_path, os.path.join(UPLOADED_DIR, video))

    except Exception as e:
        print(f"Ошибка при загрузке: {e}")


def main():
    print("Авто-загрузчик запущен...")

    while True:
        for acc in ACCOUNTS:
            run_account(acc)

        print(f"\nЖдем {DELAY_BETWEEN_UPLOADS} секунд...\n")

        for _ in range(DELAY_BETWEEN_UPLOADS):
            time.sleep(1)


if __name__ == "__main__":
    main()
