import sys
import os
import subprocess
import time
import csv
import urllib2
import pprint
import json


"""
Take status csv file from url and coordinate csv file to create 
data dictionary format and convert that format into geojson type. 
This geojson data can then be loaded into GitHub page to view
using it's mapping component

"""

"""
Input data strcture and output data structure (geojson)

Given remote rows from cso_status_data. Data when downloaded from url 
11TH.CSOSTATUS_N,3
30TH.CSOSTATUS_N,3
3RD.CSOSTATUS_N,3

And local coords in the form of
[{'CSO_TagName': 'ALKI', 'X_COORD': '-122.4225', 'Y_COORD': '47.57024'},
 {'CSO_TagName': 'ALSK', 'X_COORD': '-122.40695', 'Y_COORD': '47.55944'},
 {'CSO_TagName': 'MURR', 'X_COORD': '-122.4', 'Y_COORD': '47.54028'},...]


formatted_geojson_data_dict = {'type':'FeatureCollection','features':
[{'type':'Feature','properties':{},'geometry':{'type':'Point','coordinates':[]}}]}

NEED a Data structure template in python to look like this then convert to  GeoJSON 

{'type':'FeatureCollection",
  'features': [{'type': 'Features',
                'properties':{'CSO_TagName': 'ALKI',
                              'Value': 3},
                'geometries':{'type':'point',
                'coordinates':[-122.322,
                              47.607]}              
                }    
               ]   
}

"""

# Downloading csv status values from the web, ftp site.
cso_status_data = urllib2.urlopen("http://your.kingcounty.gov/dnrp/library/wastewater/cso/img/CSO.CSV")

# Read csv file into a python list name cso_status_csv
text = cso_status_data.readlines()
cso_status_csv = csv.reader(text)
#pprint.pprint(cso_status_csv)


#Reading CSO with Coordinate in csv file locally and create list, 
#subtitue with full data file cso_coord.csv or partial_coord.csv for two point data
cso_cord = open('partial_coord.csv', 'r')
reader = csv.DictReader(cso_cord)

location = list (reader)
cso_cord.close()
#pprint.pprint(location)


"""this the format we want to output
-question: not sure how to iterate the location object into below formatted_data_dict

formatted_geojson_data_dict = {'type':'FeatureCollection','features':
[{'type':'Feature','properties':{},'geometry':{'type':'Point','coordinates':[]}}]}

for row in location:
  formatted_geojson_data_dict['features'][row['CSO_TagName']] = 
  		{'type':'Feature',
  		'properties':{},
  		'geometry':{'coordinates':[(row['X_COORD'])],[(row['Y_COORD'])]}}
 """

#Create dictionary with geojson template
geojson_data_dict = {'type':'FeatureCollection','features':[]}


for row in location:
    # We want to populate this stub, for every row, in the location list
    # {'type':'Features','properties':{},'geometry':{'type':'Point','coordinates':[]}}
    geojson_data_dict['features'].append({'type':'Feature',
                                          'properties':{'CSO_TagName':row['CSO_TagName'],
                                                        'CSO_Status':0,'marker-color':'#666'},
                                          'geometry':{'type':'Point',
                                                      'coordinates':[float(row["X_COORD"]), float(row["Y_COORD"])]
                                                     }
                                          })


#create brand new dictionary style with color according to that status
# Value 1 = #DC143C Discharging now
# Value 2 = #FFD700 Discharged last 48 hrs
# Value 3 = #00CD00 Not Discharging
# Value 4 = #0000EE No Real Time Data
"""Did Not Work below
style_dict = {"1":{'marker-color':'#fff'},
              "4":[{'marker-color':'#0000EE'},{'Description':'No Real Time Data'}]}  

"""              
style_dict = {"1":{'marker-color':'#DC143C'},
              "2":{'marker-color':'#FFD700'},
              "3":{'marker-color':'#00CD00'},
              "4":{'marker-color':'#0000EE'}}


#??? - Not sure how to add value to be added onto geojson_data_dict object, replace with 
##default vaue of 0........
"""with help from Paul, paul helped to crated loop to add CSO_Status value
(geojson_data_dict['features'][0]) is dict
and print it returns
{'geometry':{coordinates':[-122.4225,47.57024],'type':Point'},
'properties':{'CSO_Status':0,'CSO_TagName':'ALKI'},'type':'Feature'}

Replace geojson_data_dict's one of the value with CSO status. Refer to the note.

"""

 
# Populate with station values, based on station names.
for line in cso_status_csv:
    cso_name = line[0][0:len(line[0])-12]
    CSO_Status = line[1]
    # If CSO exists, add to it.
    #Iterate through 'features' list
    for element in geojson_data_dict['features']:
      if cso_name == element['properties']['CSO_TagName']:
        element['properties']['CSO_Status'] = CSO_Status
        #element['properties'].append(style_dict[CSO_Status])
        element['properties']['marker-color']=style_dict[CSO_Status]['marker-color']

 #write out same element with additional style properties              

formatted_geojson_data_dict = json.dumps(geojson_data_dict)
pprint.pprint(formatted_geojson_data_dict)

#take formatted_geojson_data_dict file and convert '' string into a file using with open
with open('/Users/peter/Documents/KC_CSO_Status/test_file.geojson', 'w') as out_file:
   out_file.write(formatted_geojson_data_dict)


#Still need to do
#using git command to push test_file.geojson onto github
#using paul's modified code 

#subprocess.call(['git', 'add', test_file.geojson])
#  subprocess.call(['git', 'commit', '-m', '"Data Upload: ' + time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()) + '"'])
#  subprocess.call(['git', 'push'])





