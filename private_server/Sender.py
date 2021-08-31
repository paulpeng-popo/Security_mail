from PEKS.Symcrypt import *
from PEKS.Scheme import *
import hashlib, os.path, Parser

GroupCurve = "MNT224"
KeysFile = "/home/ubuntu/private_server/Server_keys"

def send(subject, message, debug=False):
	# ======= set up eliptic curve parameters =======
	groupObj = PairingGroup(GroupCurve)
	kpabe = KPabe(groupObj, debug)

	if os.path.isfile(KeysFile):
		(msk, pk) = kpabe.import_keys(KeysFile)
	else:
		(msk, pk) = kpabe.setup()
		kpabe.export_keys(msk.copy(), pk.copy(), KeysFile)
	if debug:
		print("\nmsk:\n", msk)
		print("\npk:\n", pk)

	session = groupObj.random(GT)
	data_combine = subject + "\n" + message
	data_combine = data_combine.encode('utf-8')

	# ======= AES encryption =======
	symenc = AES_EAX(session, debug)
	nonce, cipher, verf = symenc.encrypt(data_combine)
	if debug:
		print("\nnonce:\n", nonce)
		print("\ncipher:\n", cipher)
		print("\nverf:\n", verf)

	# ======= create attributes in dictionary =======
	attributes = Parser.parse_subject(subject)
	attrs = []
	for attr in attributes:
		temp = hashlib.sha224(attr.encode('utf-8')).hexdigest()
		attrs.append(temp.upper())
	if debug:
		print("\nattributes:\n", attributes)
		print("\nattrs:\n", attrs)
		print("")

	# ======= encrypt session by attributes =======
	ciphertext = kpabe.encrypt(pk, session, attrs)
	if debug: print("\nciphertext:\n", ciphertext)

	# ======= make result of encryption converted into string =======
	chead = groupE_to_base64(ciphertext.copy(), groupObj)
	subject = hashlib.sha224(nonce).hexdigest()
	outputJSON = {
		'Nonce': byte_to_base64(nonce),
		'Content': byte_to_base64(cipher),
		'Tag': byte_to_base64(verf)
	}

	json_string = json.dumps(outputJSON)
	enc_data = byte_to_base64(json_string.encode('utf-8'))
	return chead, subject, enc_data

if __name__ == "__main__":
	subject = "今天的我很開心，哈哈想不到吧。我叫彭煜博，幹專題好難，不會做。"
	message = "Today, I was so happy, because I got good grade \
on the math test.\
Yesterday, I spent $300NT on my old scooter.\
I am a happy goat.\
You know, the erath is the center of the world,\
everything is orbit around earth\
I can see Milkyway from my house rooftop.\
So excited to meet my new girlfriend, \
Am I handsome enough?"

	chead, enc_subject, enc_body = send(subject, message, False)
	print('\n'+chead)
	print('\n'+enc_subject)
	print('\n'+enc_body)
