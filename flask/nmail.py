from flask import Flask, session, render_template, make_response
from flask import jsonify, redirect, request, url_for, send_file
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os, ast, time, json, hashlib, requests
import Search, pybase64, re, calendar

DOWNLOAD_PATH = "/home/ubuntu/flask/attachments/"
CLIENT_SECRETS_FILE = "/home/ubuntu/flask/secret.json"
SCOPES = ["https://mail.google.com/"]

app = Flask(__name__)
app.secret_key = os.urandom(16)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@app.route("/")
def index():
    if 'credentials' in session:
        return redirect(url_for("mailbox"))
    return render_template("index.html")

@app.route("/authorize")
def authorize():
    if is_cookies_valid(): return redirect(url_for("mailbox"))
    verify_state = hashlib.sha256(os.urandom(1024)).hexdigest()
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes = SCOPES)
    flow.redirect_uri = "https://nsysunmail.ml/oauth2callback"
    authorization_url, state = flow.authorization_url(
        state = verify_state,
        access_type = 'offline',
        prompt = 'consent',
        include_granted_scopes = 'true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    if "state" in session: state = session['state']
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes = SCOPES, state = state)
    flow.redirect_uri = "https://nsysunmail.ml/oauth2callback"
    authorization_response = request.url
    flow.fetch_token(authorization_response = authorization_response)
    session['credentials'] = credentials_to_dict(flow.credentials)
    return set_Cookies(redirect(url_for("mailbox")))

@app.route("/inbox")
def mailbox():
    if 'credentials' in session:
        creds = Credentials.from_authorized_user_info(session['credentials'], scopes=SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        search_token = request.args.get('query')
        return display_mailbox(service, search_token=search_token)
    return redirect(url_for("index"))

def display_mailbox(service, classes="INBOX", search_token=None):
    messages_list = service.users().messages().list(userId='me', labelIds=classes).execute()
    user_info = service.users().getProfile(userId='me').execute()
    emailAddress, messagesTotal = user_info['emailAddress'], user_info['messagesTotal']

    head = ["Subject", "From", "Date", "Chead"]
    batch = service.new_batch_http_request()
    for mail in messages_list.get('messages'):
        batch.add(service.users().messages().get( userId = 'me',
                                                  id = mail['id'],
                                                  format = 'metadata',
                                                  metadataHeaders = head ))
    batch.execute()

    mailRows = []
    search_list = []
    search_buffer = []
    for request_id in batch._order:
        resp, content = batch._responses[request_id]
        message = json.loads(content)
        message_id = message['id']

        headers = message['payload']['headers']
        if len(headers) == 4 and search_token and search_token != "all":
            chead = next(item["value"] for item in headers if item["name"] == "Chead")
            search_list.append(chead)
            search_buffer.append({"headers": headers, "message_id": message_id})
        elif not search_token or search_token == "all":
            mailRows.append(get_MailInfo(headers, message_id))

    if search_token and search_token != "all":
        results = Search.search(search_list, search_token)
        for i, res in enumerate(results):
            if res:
                mailRows.append(get_MailInfo(search_buffer[i]['headers'], search_buffer[i]['message_id']))

    return render_template("inbox.html", userAddress=emailAddress,
                                         messagesTotal=messagesTotal,
                                         mailRows=mailRows,
                                         search_token=search_token    )

def get_MailInfo(headers, message_id, shrink=True):
    month_table = { month: index for index, month in enumerate(calendar.month_abbr) if month }
    week_table = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for item in headers:
        if item['name'] == "Subject":
            subject = item['value']
        if item['name'] == "From":
            sender = item['value']
        if item['name'] == "Date":
            date_str = item['value']

    date_list = date_str.split()
    diff = date_list[5]
    time_str = list(map(int, (date_list[4]).split(":")))
    year = int(date_list[3])
    month = month_table[date_list[2]]
    day = int(date_list[1])

    if len(diff) < 5: diff = "+0800"
    if diff[0] == "+": diff = 8 - int(diff[1:3])
    else: diff = 8 + int(diff[1:3])
    time = datetime(year, month, day, time_str[0], time_str[1], time_str[2])
    correct_time = time + timedelta(hours=diff)
    dayOfweek = week_table[correct_time.weekday()]

    offset = datetime.utcnow() + timedelta(hours=8) - correct_time
    yearOftoday = (datetime.utcnow() + timedelta(hours=8)).timetuple()[0]
    yearOfcorrect = correct_time.timetuple()[0]

    if shrink:
        if yearOftoday > yearOfcorrect: date_str = correct_time.strftime("%Y/%m/%d")
        elif offset >= timedelta(hours=12): date_str = correct_time.strftime("%m/%d")
        else: date_str = correct_time.strftime("%H:%M")

        sender = re.sub("<.+@.+>", "", sender)
        if sender[0] == '"': sender = sender[1:]
        if sender[-2] == '"': sender = sender[:-2]
    else:
        date_str = correct_time.strftime("%Y/%m/%d %A %H:%M")

    return {'Subject': subject, 'From': sender, 'Date': date_str, 'ID': message_id}

@app.route('/show', methods=['GET'])
def read_mail():
    if 'credentials' in session:
        creds = Credentials.from_authorized_user_info(session['credentials'], scopes=SCOPES)
        service = build('gmail', 'v1', credentials=creds)

        user_info = service.users().getProfile(userId='me').execute()
        emailAddress = user_info['emailAddress']

        message_id = request.args.get('id')
        sender, subject, date_str, mail_body, attachments, chead = get_Mailbody(service, message_id)

        search_token = request.args.get('query')
        if search_token != "None":
            decrypt_data = { "mail": mail_body, "chead": chead, "token": search_token,
                             "user": emailAddress, "sender": sender, "date": date_str,
                             "attachments": attachments }
            result = requests.post('https://owenchen.cf/decrypt', json=decrypt_data)
            if result.text:
                print("Mail decrypt successfully.")
                return redirect("https://owenchen.cf/show?random_key=" + result.text)

        return render_template("read.html", userAddress=emailAddress,
                                            SUBJECT=subject,
                                            SENDER=sender,
                                            DATE=date_str,
                                            mail_body=mail_body,
                                            attachments=attachments)
    return redirect(url_for("index"))

@app.route('/downloads/<path:filename>', methods=['GET'])
def download(filename):
    h = hashlib.blake2b(digest_size=8)
    h.update(filename.encode('utf-8'))
    hash_filename = h.hexdigest()

    path = "/home/ubuntu/flask/attachments/" + hash_filename
    return send_file(path, as_attachment=True, download_name=filename)

@app.route('/send', methods=['POST'])
def send_mail():
    send_data_json = request.get_json(force=True)
    create_credentials(send_data_json['Cookies'])
    creds = Credentials.from_authorized_user_info(session['credentials'], scopes=SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    if request.method == "POST":
        user_info = service.users().getProfile(userId='me').execute()
        sender = user_info['emailAddress']

        message = MIMEText(send_data_json['Message'])
        message['To'] = send_data_json['Receiver']
        message['From'] = sender
        message['Subject'] = send_data_json['Subject']
        message['Chead'] = send_data_json['Chead']
        raw_data = {'raw': pybase64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')}

        try:
            result = service.users().messages().send(userId='me', body=raw_data).execute()
            print(result)
            return "success"
        except Exception as error:
            print(error)
            return "fail"
    return "Method not allowed."

@app.route('/logout')
def logout():
    if 'credentials' in session:
        del session['credentials']
    resp = make_response(redirect(url_for("index")))
    # resp.set_cookie(key='gmailapi_token', value='', expires=0)
    # resp.set_cookie(key='gmailapi_refresh_token', value='', expires=0)
    return resp

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errorpage.html")

def credentials_to_dict(credentials):
    return { 'token': credentials.token,
             'refresh_token': credentials.refresh_token,
             'token_uri': credentials.token_uri,
             'client_id': credentials.client_id,
             'client_secret': credentials.client_secret,
             'scopes': credentials.scopes                 }

def create_credentials(cookies):
    with open(CLIENT_SECRETS_FILE, "r") as f:
        secrets = f.read()
    f.close()
    secrets = ast.literal_eval(secrets)['web']
    credentials = {
        'token': cookies['token'],
        'refresh_token': cookies['refresh_token'],
        'token_uri': secrets['token_uri'],
        'client_id': secrets['client_id'],
        'client_secret': secrets['client_secret'],
        'scopes': SCOPES
    }
    session['credentials'] = credentials

def is_cookies_valid():
    cookies = {}
    cookies['token'] = request.cookies.get('gmailapi_token')
    cookies['refresh_token'] = request.cookies.get('gmailapi_refresh_token')
    if (cookies['token'] != "") and (cookies['refresh_token'] != ""):
        create_credentials(cookies)
        creds = Credentials.from_authorized_user_info(session['credentials'], scopes=SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        try:
            results = service.users().messages().list(userId='me', labelIds='INBOX').execute()
        except Exception as error:
            return False
    return True

def dict_visualize(dict_data):
    tree_str = json.dumps(dict_data, indent=4)
    tree_str = tree_str.replace("\n    ", "<br />")
    tree_str = tree_str.replace('"', "")
    tree_str = tree_str.replace(',', "")
    tree_str = tree_str.replace("{", "")
    tree_str = tree_str.replace("}", "")
    tree_str = tree_str.replace("    ", " | ")
    tree_str = tree_str.replace("  ", " ")
    return tree_str

def set_Cookies(target_action):
    cookies = {}
    cookies['token'] = session['credentials']['token']
    cookies['refresh_token'] = session['credentials']['refresh_token']
    expired_time = time.time()+30*60
    resp = make_response(target_action)
    resp.set_cookie(key='gmailapi_token', value=cookies['token'], expires=expired_time)
    resp.set_cookie(key='gmailapi_refresh_token', value=cookies['refresh_token'], expires=expired_time)
    return resp

def get_Mailbody(service, message_id, debug=False):
    mail = service.users().messages().get(userId='me', id=message_id).execute()
    if debug: return dict_visualize(mail)

    payload = mail['payload']

    chead = next((item["value"] for item in payload['headers'] if item["name"] == "Chead"), None)
    header = get_MailInfo(payload['headers'], message_id, False)

    attachments_list = []
    plain_text = False
    encoded_data = ""
    image_cids = []
    if "text" in payload['mimeType']:
        if "plain" in payload['mimeType']:
            plain_text = True
        encoded_data = payload['body']['data']
    else:
        for part in payload.get('parts'):
            if ("text" in part['mimeType']) and (part['filename'] == ""):
                encoded_data = part['body']['data']
                if "plain" in part['mimeType']: plain_text = True
                else: plain_text = False
            elif "multipart" in part['mimeType']:
                for second_part in part.get('parts'):
                    if ("text" in second_part['mimeType']) and (second_part['filename'] == ""):
                        encoded_data = second_part['body']['data']
                        if "plain" in second_part['mimeType']: plain_text = True
                        else: plain_text = False
            if part['filename']:
                attachment_name = part['filename']
                if 'data' in part['body']:
                    att_data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    attachment = service.users().messages().attachments().get(userId='me', messageId=message_id, id=att_id).execute()
                    att_data = attachment['data']
                    att_size = attachment['size']

                attachments_list.append({ 'Name': attachment_name, 'Size': att_size, "File_url": "https://nsysunmail.ml/downloads/" + attachment_name })
                file_data = pybase64.urlsafe_b64decode(att_data.encode('UTF-8'))

                att_data = att_data.replace("-","+").replace("_","/")
                for item in part['headers']:
                    if item['name'] == 'Content-ID' and item['value']:
                        image_cids.append({ "cid": item['value'], "type": part['mimeType'], "dataBASE64": att_data })
                    elif item['name'] == 'X-Attachment-Id' and item['value']:
                        image_cids.append({ "cid": item['value'], "type": part['mimeType'], "dataBASE64": att_data })

                h = hashlib.blake2b(digest_size=8)
                h.update(attachment_name.encode('utf-8'))
                name = h.hexdigest()
                filepath = DOWNLOAD_PATH + name
                with open(filepath, "wb") as f:
                    f.write(file_data)
                f.close()

    if not encoded_data:
        return "Mail data fetch error."

    data = encoded_data.replace("-","+").replace("_","/")
    decoded_data = pybase64.urlsafe_b64decode(data)

    body = decoded_data.decode('utf-8')
    if plain_text:
        body = body.replace("\r\n", "<br />")

    for item in image_cids:
        be_sub = "cid:" + item['cid']
        newSRC = "data:" + item['type'] + ";base64, " + item['dataBASE64']
        body = re.sub(be_sub, newSRC, body)

    return header['From'], header['Subject'], header['Date'], body, attachments_list, chead
