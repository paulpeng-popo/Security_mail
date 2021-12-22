from flask import Flask, request, redirect, render_template, send_file
from PrivateLib.PEKS.Othertools.utils import base64_to_byte, byte_to_base64
from werkzeug.datastructures import FileStorage
from PrivateLib.Receiver import *
from PrivateLib.Sender import *
from PrivateLib.Parser import *
import os, hashlib, requests

app = Flask(__name__)
UPLOAD_FOLDER = '/home/ubuntu/private_server/attachments/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
messages = {}

@app.route("/parse", methods=['GET'])
def subject_parse():
	subject = request.args.get('subject')
	attributes = parse_subject(subject)
	attr_demo = { 'response': attributes }
	return attr_demo

@app.route("/compose", methods=['GET', 'POST'])
def compose():
	if request.method == 'GET':
		token = request.args.get('token')
		refresh_token = request.args.get('refresh_token')
		return render_template("compose.html", token=token, refresh_token=refresh_token)

	form_data = request.form
	receiver = form_data.get('to', None)
	cc_receivers = form_data.get('cc', None)
	subject = form_data.get('subject', None)
	attributs = form_data.get('AttrsList[]', None)
	message = form_data.get('message', None)
	files = request.files.getlist('attachments[]', None)

	print(attributs.split(','))

	if cc_receivers:
		cc_receivers.replace(' ', '')
		cc_receivers = cc_receivers.split(',')

	the_attachments = None
	if files[0].filename:
		the_attachments = []
		for file in files:
			h = hashlib.blake2b(digest_size=8)
			h.update(file.filename.encode('utf-8'))
			hash_filename = h.hexdigest()
			file.save(os.path.join(UPLOAD_FOLDER, hash_filename))

			with open(os.path.join(UPLOAD_FOLDER, hash_filename), 'rb') as f:
				data = f.read()
			f.close()

			fchead, enc_fakename, enc_fdata = send(file.filename, byte_to_base64(data))
			the_attachments.append( { 'name': file.filename, 'header': fchead, 'value': enc_fdata } )

	cookies = {}
	cookies['token'] = form_data['Cookies_token']
	cookies['refresh_token'] = form_data['Cookies_refresh_token']

	chead, enc_subject, enc_body = send(subject, message, AttrsList=attributs.split(','))
	
	sending_data = { "Cookies": cookies, "Receiver": receiver, "Cc": cc_receivers,
					 "Subject": enc_subject, "Message": enc_body,
					 "Chead": chead, "Attachments": the_attachments }
	result = requests.post('https://nsysunmail.ml/send', json=sending_data)

	if result.text == "success":
		print("Mail sends successfully.")
		return redirect("https://nsysunmail.ml/")
	else: return "Sorry,<br />Your authorization is expired,<br />please <a href='https://nsysunmail.ml'>re-authorize</a> and compose again !!"

@app.route("/show")
def show():
	random_key = request.args.get('random_key')
	if random_key in messages:
		return render_template("read.html", userAddress=messages[random_key]['User'],
                         					Receiver=messages[random_key]['Receiver'],
											SUBJECT=messages[random_key]['Subject'],
											SENDER=messages[random_key]['Sender'],
											DATE=messages[random_key]['Date'],
											mail_body=messages[random_key]['Message'],
											attachments=messages[random_key]['Attachments']                    )
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
	receiver = enc_data['receiver']
	date_str = enc_data['date']
	search_token = enc_data['token']
	attachments_list = enc_data['attachments']

	for file in attachments_list:
		d_index = file['Content'].find('\n')
		header = file['Content'][:d_index]
		value = file['Content'][d_index:]
		search_word = parse_subject(file['Name'])
		search_word = ' '.join(search_word)
		file_search_token = tokenGen(search_word)
		file_name, file_content = unlock_mail(header, file_search_token, value)
		file['File_url'] = "https://owenchen.cf/downloads/" + file_name
		file['Content'] = None

		h = hashlib.blake2b(digest_size=8)
		h.update(file_name.encode('utf-8'))
		name = h.hexdigest()
		filepath = UPLOAD_FOLDER + name
		with open(filepath, "wb") as f:
			f.write(base64_to_byte(file_content))
		f.close()

	subject, message = unlock_mail(chead, search_token, mail_body)
	decrypted_data = {
						"Subject": subject,
						"Message": message,
						"User": user,
						"Sender": sender,
						"Receiver": receiver,
						"Date": date_str,
						"Attachments": attachments_list
					 }
	messages[random_key] = decrypted_data
	return random_key

@app.route('/downloads/<path:filename>', methods=['GET'])
def download(filename):
	h = hashlib.blake2b(digest_size=8)
	h.update(filename.encode('utf-8'))
	hash_filename = h.hexdigest()

	path = "/home/ubuntu/private_server/attachments/" + hash_filename
	return send_file(path, as_attachment=True, download_name=filename)

@app.route("/GetSearchToken", methods=['POST'])
def generate_token():
	form_data = (request.form)['query']
	classes = (request.form)['classes']
	if form_data == "@all": return redirect('https://nsysunmail.ml/inbox/'+classes+'?query=all')
	search_token = tokenGen(form_data)
	print("Token generates successfully.")
	search_url = 'https://nsysunmail.ml/inbox/'+classes+'?query=' + search_token
	return redirect(search_url)
