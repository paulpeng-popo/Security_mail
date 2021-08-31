from flask import Flask, request, redirect
from flask import render_template
import requests, Sender, Receiver

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, I am Owen Chen."

@app.route("/happy")
def happy():
    return "I am so happy today, balabala..."

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
    search_token = Receiver.tokenGen(form_data)
    print("Token generates successfully.")
    search_url = 'https://nsysunmail.ml/inbox?query=' + search_token
    return redirect(search_url)
