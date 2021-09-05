from charm.toolbox.pairinggroup import PairingGroup
from charm.toolbox.secretutil import SecretUtil
from PrivateLib.PEKS.Othertools.utils import *

def search(data, search_key):
	# ======= get encrypted data =======
	groupObj = PairingGroup("MNT224")
	util = SecretUtil(groupObj, False)

	data = base64_to_groupE(data, groupObj)
	search_key = base64_to_groupE(search_key, groupObj)

	policy = util.createPolicy(search_key['policy'])
	attrs = util.prune(policy, data['attributes'])
	if attrs == False: return False
	return True
