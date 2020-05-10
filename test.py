from OCR import OCR

OCR = OCR()
OCR.setExecPath('C:/Program Files (x86)/Tesseract-OCR/tesseract')

OCR.loadImage('images/a.png')
results, image = OCR.process()
OCR.saveImage('b_r')

correction = ['Gnosis', 'Gila', 'Imicus', 'Caracal', 'Caracal', 'Widow', 'Dramiel', 'Bellicose', 'Velator', 'Ibis', 'Capsule', 'Prowler', 'Occator', 'Crane', 'Gila', 'Gnosis', 'Badger', 'Gnosis', 'Venture', 'Prophecy', 'Buzzard', 'Algos', 'Malediction', 'Osprey Navy Issue', 'Praxis', 'Gila', 'Rifter', 'Apotheosis', 'Condor', 'Tornado', 'Maelstrom', 'Maelstrom', 'Tengu', 'Gnosis', 'Caracal', 'Amarr Shuttle', 'Gnosis', 'Impairor', 'Gila', 'Hyperion', 'Bowhead', 'Federation Navy Comet', 'Obelisk', 'Harpy', 'Mastodon',
'Shifz0r', 'York Ichinumi', 'Zealousy Solaris', 'verlander Sunji', 'Jamie Yao', 'Moby Castlman', 'Chromis Nigripinnis', 'Itsinfoot', 'traporte dinero', 'Auleway', 'Dewblara Grindo', 'Kurenai Uchiha', 'lilian Senbonza', 'DoctorPooh', 'Jikstra', 'janus4x Estemaire', 'Mista Zoog', 'arbalesttom', 'Dmyruy Protasevich', 'Jace Ozran', 'Hamtai', 'Octavius Paladin', 'Felix Tekwar', 'Raya en Distel', 'Octavia Panacan', 'Ruslan Storozhuk', 'Jim Coalback', 'Hela Larva', 'Arch Spotter', 'Cron Usoko', 'Pinzettman', 'FroschBosch', 'Igor Kegebist', 'sorryforyourloss', 'Endiron', 'lexx Min', 'Desire Arbalest', 'Gach Heang Acami', 'Natali Globus', 'Raymond Tiboteau', 'Div', 'Gabriel Palo', 'Daxter Octavius', 'AzoV Isu', 'Mowzie Moliko']

count=0
for i,r in enumerate(results):
	if correction[i] != r:
		print('Error with {} > {}'.format(r,correction[i]))
		count += 1

print("Error count: "+ str(count))
#print (results)
