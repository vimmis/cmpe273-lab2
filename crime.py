from spyne import Application, rpc, ServiceBase, Float, Unicode
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
from spyne.decorator import srpc
import urllib, json
from collections import Counter
import logging
logging.basicConfig(level=logging.DEBUG)

class Crime(ServiceBase):
	@srpc(Float,Float,Float, _returns=Unicode)
	def checkcrime(lat,lon, radius):
		url = "https://api.spotcrime.com/crimes.json?lat={0}&lon={1}&radius={2}&key=.".format(lat,lon,radius)
		response = urllib.urlopen(url)
		input_json = json.loads(response.read())
		crime_sets= input_json["crimes"]
		event_time_count ={"12:01am-3am" : 0,"3:01am-6am" : 0,"6:01am-9am" : 0,"9:01am-12noon" : 0,"12:01pm-3pm" : 0,"3:01pm-6pm" : 0,"6:01pm-9pm" : 0,"9:01pm-12midnight" : 0} 
		crime_type_count={}
		crime_street={}
		total_crime = 0
		for result in crime_sets:
			total_crime += 1
			if result["type"] in crime_type_count.keys():
				crime_type_count[result["type"]]+= 1
			else:
				crime_type_count[result["type"]]= 1
			d =result["date"]
			if d[9:11] =="12" and int(d[12:15])==0 and d[15:] =="AM":
				event_time_count["9:01pm-12midnight"]+=1
			elif d[15:] =="PM":
				if (d[9:11] =="12" and int(d[12:15])>0) or (int(d[9:11])>=1 and int(d[9:11])<3) or (d[9:11]=="03" and d[12:15]=="00"):
					event_time_count["12:01pm-3pm"]+=1
				elif (int(d[9:11])>=3 and int(d[9:11])<6) or (d[9:11]=="06" and d[12:15]=="00"):
					event_time_count["3:01pm-6pm"]+=1
				elif (int(d[9:11])>=6 and int(d[9:11])<9) or (d[9:11]=="09" and d[12:15]=="00"):
					event_time_count["6:01pm-9pm"]+=1
				else:
					event_time_count["9:01pm-12midnight"]+=1
			elif d[15:] =="AM":
				if (d[9:11] =="12" and int(d[12:15])>=0) or (int(d[9:11])>=1 and int(d[9:11])<3) or (d[9:11]=="03" and d[12:15]=="00"):
					event_time_count["12:01am-3am"]+=1					
				elif (int(d[9:11])>=3 and int(d[9:11])<6) or (d[9:11]=="06" and d[12:15]=="00"):
					event_time_count["3:01am-6am"]+=1
				elif (int(d[9:11])>=6 and int(d[9:11])<9) or (d[9:11]=="09" and d[12:15]=="00"):
					event_time_count["6:01am-9am"]+=1
				else:
					event_time_count["9:01am-12noon"]+=1
	
			address= result["address"]
			if " BLOCK BLOCK " in address:
				street = (address.split("BLOCK BLOCK",1)[1]).strip()
				if street in crime_street.keys():
					crime_street[street]+= 1
				else:
					crime_street[street]= 1
			elif " BLOCK OF " in address:
				street = (address.split("BLOCK OF",1)[1]).strip()
				if street in crime_street.keys():
					crime_street[street]+= 1
				else:
					crime_street[street]= 1 
			elif "&" in address:
				street1 = (address.split("&",2)[0]).strip()
				street2 = (address.split("&",2)[1]).strip()
				if street1 in crime_street.keys():
					crime_street[street1]+= 1
				else:
					crime_street[street1]= 1 
				if street2 in crime_street.keys():
					crime_street[street2]+= 1
				else:
					crime_street[street2]= 1 
			elif " AND " in address:
				street1 = str((address.split(" AND ",2)[0]).strip())
				street2 = str((address.split(" AND ",2)[1]).strip())
				if street1 in crime_street.keys():
					crime_street[street1]+= 1
				else:
					crime_street[street1]= 1 
				if street2 in crime_street.keys():
					crime_street[street2]+= 1
				else:
					crime_street[street2]= 1 
			elif " BLOCK " in address:
				street = (address.split(" BLOCK ",1)[1]).strip()
				if street in crime_street.keys():
					crime_street[street]+= 1
				else:
					crime_street[street]= 1
			elif "//" in address:
				street1 = (address.split("//",2)[0]).strip()
				street2 = (address.split("//",2)[1]).strip()
				if street1 in crime_street.keys():
					crime_street[street1]+= 1
				else:
					crime_street[street1]= 1 
				if street2 in crime_street.keys():
					crime_street[street2]+= 1
				else:
					crime_street[street2]= 1 
			elif "/" in address:
				street1 = (address.split("/",2)[0]).strip()
				street2 = (address.split("/",2)[1]).strip()
				if street1 in crime_street.keys():
					crime_street[street1]+= 1
				else:
					crime_street[street1]= 1 
				if street2 in crime_street.keys():
					crime_street[street2]+= 1
				else:
					crime_street[street2]= 1 
			else:
				if address in crime_street.keys():
					crime_street[address]+= 1
				else:
					crime_street[address]= 1
		
		top3streets = {}
		st = Counter(crime_street)
		for k,v in st.most_common(3):
			top3streets[k] =v
	
		return ({
			"total_crime" : total_crime,
			"the_most_dangerous_streets" : top3streets.keys(),
			"crime_type_count" :crime_type_count, 
			"event_time_count" :event_time_count,
			#"all streets:":crime_street
			})
	
		        
application = Application([Crime],
	tns='cmpe273.lab2.crime',
	in_protocol=HttpRpc(validator='soft'), 	
	out_protocol=JsonDocument()
)
if __name__ == '__main__':
	
    # Using Python's built-in wsgi server
	from wsgiref.simple_server import make_server
	wsgi_app = WsgiApplication(application)
	server = make_server('0.0.0.0', 8000, wsgi_app)
	server.serve_forever()
