from charm.toolbox.pairinggroup import PairingGroup
from charm.toolbox.secretutil import SecretUtil
from LibServer.Othertools.utils import *

groupObj = PairingGroup("MNT224")
util = SecretUtil(groupObj, False)

def search(data_list, search_key):
	data_list_groupE = []
	for data in data_list:
		data_list_groupE.append(base64_to_groupE(data, groupObj))

	search_key = base64_to_groupE(search_key, groupObj)
	policy = util.createPolicy(search_key['policy'])

	results = []
	for data_groupE in data_list_groupE:
		attrs = util.prune(policy, data_groupE['attributes'])
		if attrs == False: results.append(False)
		else: results.append(True)
	return results
