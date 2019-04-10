from __future__ import print_function
import pickle
import os.path

import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.metadata']


# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1isYvdlAMZfkyanuixswO7-t6rC-dtP2B6Lq2VzxjmQk'
RESPONSE_RANGE = 'Form Responses 1!A2:L'

PROCESSED_RANGE = 'Processed!A2:L'


FOLDER_ID = '0B3lDOqQBiLPYflQ5R195aE5qaHlRV09uMmE2YmY0UWRoazJmWUQwYThxZ0pEcjljeFN3WE0'



def print_files_in_folder(service, folder_id):

    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token

            children = service.children().list(folderId=folder_id, **param).execute()

            for child in children.get('items', []):

                childId = child['childLink'].split('/')[-1]

                file = service.files().get(fileId=childId).execute()

                print(f"File Id: {child['id']} - {file['title']}")

            page_token = children.get('nextPageToken')

            if not page_token:
                break

        except errors.HttpError as error:
            print(f"An error occurred: {error}")
            break



def viewFiles(creds):

    service = build('drive', 'v2', credentials=creds)

    print_files_in_folder(service, FOLDER_ID)
    # # Call the Drive v3 API
    # results = service.files().list(
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()

    # items = results.get('files', [])

    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))

def viewSpreadsheet(creds):

    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RESPONSE_RANGE).execute()

    values = result.get('values', [])

    drive = build('drive', 'v2', credentials=creds)


    if not values:
        print('No new reciepts found.')
    else:
        #print('Name, Major:')
        for row in values:
            if(len(row) == 0): continue

            # Print columns A and E, which correspond to indices 0 and 4.
            print(f"{row[1]} - {row[2]} - {row[3]} - {row[4]} - {row[5]} - ${row[6]} - UNPAID")
           
            name = f"{row[2]} {row[3]}"

            date_time_obj = datetime.datetime.strptime(row[4], '%d/%m/%Y')

            date = f"{date_time_obj.strftime('%d.%m.%y')}"

            #date = f"{date_time_obj.date().day}.{date_time_obj.date().month}.{date_time_obj.date().year}"

            print(f"Date is: {date}")

            file_id = row[1].split('/')[-1].split('=')[-1]

            original_title = get_file_title(drive, file_id)

            rename_file(drive, file_id, f"{name} - {date} - {row[5]} - ${row[6]} - UNPAID")

            new_title = get_file_title(drive, file_id)

            print(f"Renamed: {original_title} -> {new_title}")




        body = {'values': values}

        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=PROCESSED_RANGE,
            valueInputOption='RAW', body=body).execute()

        print(f"{result.get('updates').get('updatedCells')} cells appended.")

        result = service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range=RESPONSE_RANGE).execute()
        print(f"Cleared Responses - Range Cleared: {result.get('clearedRange')}")

def get_file_title(service, file_id):
    try:
    # First retrieve the file from the API.
        file = service.files().get(fileId=file_id).execute()

        return(file['title'])
  
    except errors.HttpError as error:
        print(f'An error occurred: {error}')
        return None

def rename_file(service, file_id, new_title):
 
    try:
        # First retrieve the file from the API.
        file = service.files().get(fileId=file_id).execute()

        # File's new metadata.
        file['title'] = new_title + "." + file['mimeType'].split('/')[-1]

        # Send the request to the API.
        updated_file = service.files().update(fileId=file_id,body=file).execute()
        return updated_file
  
    except errors.HttpError as error:
        print(f'An error occurred: {error}')
        return None



def getCreds():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def main():
    
    creds = getCreds()
    
    viewSpreadsheet(creds)
    #viewFiles(creds)
    #test(creds)




if __name__ == '__main__':
    main()