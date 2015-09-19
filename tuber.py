from urllib2 import Request, urlopen, URLError
from secret import *

context = 'koko ithaca,ny to ctb ithaca,ny'

query = context.split("to")
ori = query[0].strip().replace(' ','+')
des = query[1].strip().replace(' ','+')
request = Request('https://maps.googleapis.com/maps/api/place/textsearch/xml?query='+ori+'&key='+key)
request2 = Request('https://maps.googleapis.com/maps/api/place/textsearch/xml?query='+des+'&key='+key)

def main():
	try:
		response = urlopen(request)
		result = response.read()

		lat_begin = result.find('<lat>')
		lat_end = result.find('</lat>')
		lat = result[lat_begin+5:lat_end]	

		lng_begin = result.find('<lng>')
		lng_end = result.find('</lng>')
		lng = result[lng_begin+5:lng_end]

		print lat
		print lng

	except URLError as e:
		print ('error'), e
	try:
		response = urlopen(request2)
		result = response.read()

		lat_begin = result.find('<lat>')
		lat_end = result.find('</lat>')
		lat = result[lat_begin+5:lat_end]	

		lng_begin = result.find('<lng>')
		lng_end = result.find('</lng>')
		lng = result[lng_begin+5:lng_end]

		print lat
		print lng

	except URLError as e:
		print ('error'), e
if __name__ == '__main__':
	main()
