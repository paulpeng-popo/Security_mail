from flask import Flask, request, redirect
from flask import render_template
import requests, Sender, Receiver
import os, hashlib

app = Flask(__name__)
messages = {}

@app.route("/show")
def show():
    random_key = request.args.get('random_key')
    if random_key in messages:
        return render_template("read.html", userAddress=messages[random_key]['User'],
                                            SUBJECT=messages[random_key]['Subject'],
                                            SENDER=messages[random_key]['Sender'],
                                            DATE=messages[random_key]['Date'],
                                            mail_body=messages[random_key]['Message'])
    else:
        return redirect("https://nsysunmail.ml/404")

@app.route("/decrypt", methods=['POST'])
def decrypt():
    random_key = os.urandom(16)
    random_key = hashlib.sha224(random_key).hexdigest()

    enc_data = request.get_json(force=True)
    mail_body = enc_data['mail']
    chead = enc_data['chead']
    user = enc_data['user']
    sender = enc_data['sender']
    date_str = enc_data['date']
    search_token = enc_data['token']

    subject, message = Receiver.unlock_mail(chead, search_token, mail_body)
    decrypted_data = {
                        "Subject": subject,
                        "Message": message,
                        "User": user,
                        "Sender": sender,
                        "Date": date_str
                     }
    messages[random_key] = decrypted_data
    return random_key

@app.route("/encrypt", methods=['POST'])
def encrypt():
    form_data = request.form

    receiver = form_data['to']
    subject = form_data['subject']
    message = form_data['message']

    chead, enc_subject, enc_body = Sender.send(subject, message)

    cookies = {}
    cookies['token'] = form_data['Cookies_token']
    cookies['refresh_token'] = form_data['Cookies_refresh_token']

    sending_data = {"Cookies": cookies, "Receiver": receiver, "Subject": enc_subject, "Message": enc_body, "Chead": chead}
    result = requests.post('https://nsysunmail.ml/send', json=sending_data)

    if result.text == "success":
        print("Mail sends successfully.")
        return redirect("https://nsysunmail.ml/")
    else: return "Something bad happened when sending mail."

@app.route("/GetSearchToken", methods=['POST'])
def generate_token():
    form_data = (request.form)['query']
    if form_data == "@all": return redirect('https://nsysunmail.ml/inbox?query=all')
    search_token = Receiver.tokenGen(form_data)
    print("Token generates successfully.")
    search_url = 'https://nsysunmail.ml/inbox?query=' + search_token
    return redirect(search_url)
