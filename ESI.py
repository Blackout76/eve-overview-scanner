import urllib.request, urllib.error
import json

#doc: https://docs.esi.evetech.net/
#endpoints: https://esi.evetech.net/ui/

ESI_SEARCH_CHARATER = 'https://esi.evetech.net/v2/search/?categories=character&datasource=tranquility&language=en-us&search={}&strict=true'
ESI_CORPORATION = 'https://esi.evetech.net/v4/corporations/{}/?datasource=tranquility'
ESI_ALLIANCE = 'https://esi.evetech.net/v3/alliances/{}/?datasource=tranquility'
ESI_CHARACTER = 'https://esi.evetech.net/v4/characters/{}/?datasource=tranquility'

def request(url):
	try:
		return json.loads(urllib.request.urlopen(url).read().decode('utf8'))
	except urllib.error.HTTPError as err:
		print("[ESI] erreur: " + url)
		print(err)

def getPilotIDFromName(name):
	url = ESI_SEARCH_CHARATER.format(name).replace(" ", "%20")
	contents = request(url)
	if contents:
		if "character" in contents.keys():
			return contents['character'][0]

def getPilot(id):
	url = ESI_CHARACTER.format(id).replace(" ", "%20")
	contents = request(url)
	if contents:
		if len(contents.keys()) > 0:
			return contents

def getCorporation(id):
	url = ESI_CORPORATION.format(id).replace(" ", "%20")
	contents = request(url)
	if contents:
		if len(contents.keys()) > 0:
			return contents

def getAlliance(id):
	url = ESI_ALLIANCE.format(id).replace(" ", "%20")
	contents = request(url)
	if contents:
		if len(contents.keys()) > 0:
			return contents