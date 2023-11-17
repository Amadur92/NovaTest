import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaInMemoryUpload

from .models import UploadedFile
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build




@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        data = request.POST.get('data', '')
        name = request.POST.get('name', '')

        # Save to db
        uploaded_document = UploadedFile(name=name, data=data)
        uploaded_document.save()
        SCOPES = ['https://www.googleapis.com/auth/documents',
                  'https://www.googleapis.com/auth/drive']
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'google_doc_app/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
                with open('token.json', 'w') as token:
                  token.write(creds.to_json())
        drive_service = build('drive', 'v3', credentials=creds)
        # Create Metadata
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.document'
        }
        # Convert to bytes
        data_bytes = data.encode('utf-8')
        media = MediaInMemoryUpload(data_bytes, mimetype='text/plain', resumable=True)

        # Load data to Google Drive
        document = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return JsonResponse({'document_id': document['id'], 'name': name, 'data': data})
    else:
        return JsonResponse({'text': 'default'})
    return JsonResponse({'error': 'Invalid request method'})
