import json
from django.test import Client, TestCase
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google_auth_oauthlib.flow import InstalledAppFlow

from .models import UploadedFile

class UploadFileTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_file(self):
        # Test data
        data = "Текстовое содержимое файла"
        name = "test_file"

        # Creating POST-request
        response = self.client.post('/upload/', {'data': data, 'name': name})
        # Check status
        self.assertEqual(response.status_code, 200)

        # Check data
        response_data = json.loads(response.content)
        self.assertIn('document_id', response_data)
        self.assertIn('name', response_data)
        self.assertIn('data', response_data)

        # Check db
        uploaded_file = UploadedFile.objects.get(name=name)
        self.assertEqual(uploaded_file.data, data)

        # Check Google Drive
        SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)

        document_id = response_data['document_id']
        document = drive_service.files().get(fileId=document_id).execute()

        self.assertEqual(document['name'], name)
        #Clean after test
        drive_service.files().delete(fileId=document_id).execute()
