from apiclient.http import MediaFileUpload
from datetime import datetime
from docassemble.base.util import get_config
from google.oauth2 import service_account
from googleapiclient.discovery import build
from gspread import authorize
from json import loads
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

__all__ = ["new_entry"]

credential_info = loads(get_config("google").get('service account credentials'), strict=False)

def new_entry(sheet_name: str, folder_id: str, name: str, doc_name: str, doc_type: str, doc_id: str, document, worksheet_index=0):
  """
  Adds a new upload entry to the Google Spreadsheet identified by sheet_name

  The entry has the following form:
  """
  creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
  client = authorize(creds)
  sheet = client.open(sheet_name).get_worksheet(worksheet_index)
  now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
  sheet.append_row([now, name, doc_name, doc_type, doc_id])

  service = build('drive', 'v3', credentials=creds)

  file_metadata = {
      'name': f"{name}_{now}.pdf",
      'parents': [folder_id]
  }

  media = MediaFileUpload(document.path(),
                          mimetype='application/pdf',
                          resumable=True)
  file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
