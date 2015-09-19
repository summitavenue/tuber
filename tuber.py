from urllib2 import Request, urlopen, URLError
from secret import *

def get_location(context):
	query = context.split("to")
	ori = query[0].strip().replace(' ','+')
	des = query[1].strip().replace(' ','+')
	request = Request('https://maps.googleapis.com/maps/api/place/textsearch/xml?query='+ori+'&key='+key)
	request2 = Request('https://maps.googleapis.com/maps/api/place/textsearch/xml?query='+des+'&key='+key)


	try:
		response = urlopen(request)
		result = response.read()

		lat_begin = result.find('<lat>')
		lat_end = result.find('</lat>')
		ori_lat = result[lat_begin+5:lat_end]	

		lng_begin = result.find('<lng>')
		lng_end = result.find('</lng>')
		ori_lng = result[lng_begin+5:lng_end]

	except URLError as e:
		print ('error'), e
	try:
		response = urlopen(request2)
		result = response.read()

		lat_begin = result.find('<lat>')
		lat_end = result.find('</lat>')
		des_lat = result[lat_begin+5:lat_end]	

		lng_begin = result.find('<lng>')
		lng_end = result.find('</lng>')
		des_lng = result[lng_begin+5:lng_end]

	except URLError as e:
		print ('error'), e

