from urllib2 import Request, urlopen, URLError

request = Request('https://maps.googleapis.com/maps/api/place/textsearch/xml?query=koko+ithaca+NY&key=AIzaSyD0QJ-Ns43_OkJIjzzcHGSM2guT1l2qMwk')

def main():
	print ("herro world")
	try:
		response = urlopen(request)
		result = response.read()
		print (result)

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
	