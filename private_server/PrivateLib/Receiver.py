from PrivateLib.PEKS.Symcrypt import *
from PrivateLib.PEKS.Scheme import *
import ast, hashlib

GroupCurve = "MNT224"
KeysFile = "/home/ubuntu/private_server/PrivateLib/Server_keys"

def tokenGen(policy, debug=False):
	# ======= set up eliptic curve parameters =======
	groupObj = PairingGroup(GroupCurve)
	kpabe = KPabe(groupObj, debug)
	try:
		(msk, pk) = kpabe.import_keys(KeysFile)
		if debug:
			print("\nmsk:\n", msk)
			print("\npk:\n", pk)
	except Exception:
		print("\nFile: \"%s\" notfound.\n" % KeysFile)
		exit(1)

	# ======= generate search token =======
	policy_str = ""
	policy = policy.split()
	for i in range(len(policy)):
		temp = hashlib.sha224((policy[i]).encode('utf-8')).hexdigest()
		if i == len(policy)-1: policy_str += temp
		else: policy_str += temp + " or "

	search_key = kpabe.keygen(pk, msk, policy_str)
	if debug: print("\nSearch token:\n", search_key)
	search_key_base64 = groupE_to_base64(search_key.copy(), groupObj)
	if debug: print("\nSearch token base64:\n", search_key_base64)
	return search_key_base64

def unlock_mail(data, search_key, enc_body, debug=False):
	# ======= get encrypted data =======
	groupObj = PairingGroup(GroupCurve)
	kpabe = KPabe(groupObj, debug)

	data = base64_to_groupE(data, groupObj)
	search_key = base64_to_groupE(search_key, groupObj)
	enc_body = base64_to_byte(enc_body).decode('utf-8')
	enc_body = ast.literal_eval(enc_body)

	Nonce = base64_to_byte(enc_body['Nonce'])
	Content = base64_to_byte(enc_body['Content'])
	Tag = base64_to_byte(enc_body['Tag'])

	session = kpabe.decrypt(data, search_key)
	symenc = AES_EAX(session, debug)
	dec_body = symenc.decrypt(Nonce, Content, Tag)
	dec_body = dec_body.decode('utf-8')

	subject = dec_body[:dec_body.find('\n')]
	message = dec_body[dec_body.find('\n'):]

	return subject, message
