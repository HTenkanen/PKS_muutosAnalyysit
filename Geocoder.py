__author__ = 'tenkahen'
# -*- coding: utf-8 -*-
import geocoder, webbrowser, warnings, time
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd

def geocode(location, provider='google', display_map=False):

    # Try to find the location 10 times before raising the warning and returning coordinates (0.0, 0.0)
    i = 0
    while True:
        if provider == 'google':
            geo = geocoder.google(location)
        elif provider == 'nokia':
            geo = geocoder.nokia(location)
        elif provider == 'osm':
            geo = geocoder.osm(location)
        elif provider == 'bing':
            if location.replace(',', '').replace('.', '').replace('-', '').isdigit():
                geo = geocoder.bing_reverse.BingReverse(location)
            else:
                geo = geocoder.bing(location)
        elif provider == 'tomtom':
            geo = geocoder.tomtom(location)
        elif provider == 'arcgis':
            geo = geocoder.arcgis(location)

        if geo.json['status'] == 'OK' or i == 10:
            break
        i+=1

    #print geo.json

    if display_map == True:
        #Check if address is a coordinate pair
        if location.replace(',', '').replace('.', '').replace('-', '').isdigit():
            url = "http://maps.google.com/?q=%s" % geo.address
        else:
            url = "http://www.google.com/maps/place/%s,%s" % (geo.lat, geo.lng)
        webbrowser.open(url)

    if geo.json['status'] == 'OK':
        #time.sleep(0.5) # Try to avoid the rate limit
        return geo.json
    else:
        warn = 'WARNING: %s was not found! Coordinates (0.0, 0.0) was returned instead.' % location
        warnings.warn(warn)
        #time.sleep(0.5) # Try to avoid the rate limit
        return {'lat': 0.0, 'lng': 0.0}

def geomPoint(lat, lon):
    return Point(lon, lat)

def addressToPoint(address, provider, display_map):
    location = geocode(address, provider=provider, display_map=display_map)
    return geomPoint(location['lat'], location['lng'])

def coordToAddress(coordinates, provider, display_map):
    location = geocode(coordinates, provider=provider, display_map=display_map)
    return location['address']

def iterator(row, column, type, provider, display_map):
    if type == 'address':
        return addressToPoint(row[column], provider=provider, display_map=display_map)
    elif type == 'coordinates':
        return coordToAddress(row[column], provider=provider, display_map=display_map)
    else:
        raise ValueError("Invalid input column type! Need to be either 'address' or 'coordinates'.")

def geolocator(dataFrame, inputType, locCol, destCol, provider='google', display_map=False): #Default provider is 'google'
    data = dataFrame
    data[destCol] = data.apply(iterator, axis=1, column=locCol, type=inputType, provider=provider, display_map=display_map)
    return data


def main ():

    # Get coordinates of an address or address of a 'lat, lon' (e.g. '60.1726, 24.9510') --> only 'google' for now
    # If display_map parameter is True, it opens the geocoded location in a web browser using google maps

    #----------------------------------------------
    # Geocode single address or coordinate pair
    #----------------------------------------------

    # Geocode individual address and show the result on map
    #result = geocode("Kokkosaarenkatu 6, Helsinki", display_map=True, provider='bing')

    # Geocode a coordinate pair and print out the address (available providers: 'google' & 'bing') --> 'bing_reverse' does not work correctly at the moment --> Issue raised
    #result2 = geocode("60.2052498,24.9738293", display_map=False, provider='google')

    # Print out all of the information (result is a Python dictionary)
    #print result2

    # Print out only specific attribute from the dictionary
    #print result2['address']

    #---------------------------------------------------------------------------------------
    # Geocode multiple addresses and make a shapefile from them (using (geo)pandas approach)
    #---------------------------------------------------------------------------------------

    # Read data in (this example is from excel file)
    fp = r"C:\HY-Data\HENTENKA\KoiraTutkimus\OsoitteetKakkakarttaan.xls"
    data = pd.read_excel(fp)

    # Set prevailing zeros to fill ZIP-codes, e.g. 530 --> 00530
    data['Postinumero'] = data['Postinumero'].apply(lambda x: str(x).zfill(5))

    #Rename too long attribute names (max 10 characters)
    data.columns = [u'Omistaja', u'Lahiosoite', u'Postinum', u'Postitoim', u'KoiraNimi', u'KoiraRotu']

    #Create as good as possible address name: e.g. ExampleStreet 22, 00150 Helsinki, Finland
    data['address'] = data['Lahiosoite'] + ', ' + data['Postinum'] + ' ' + data['Postitoim'] + ', Finland'

    #Geolocate addresses
    data = geolocator(data, inputType='address', locCol='address', destCol='geometry', provider='arcgis', display_map=True)  # Available providers: 'google', 'nokia', 'tomtom', 'arcgis', 'osm', 'bing' --> same as 'nokia'

    #Determine coordinate system for the data (almost always WGS84)
    coordsys = {u'no_defs': True, u'datum': u'WGS84', u'proj': u'longlat'}

    #Create geodataframe from the results
    geo = gpd.GeoDataFrame(data, geometry='geometry', crs=coordsys)

    #out = r"...\GeocodedLocations.shp"
    #geo.to_file(out, driver="ESRI Shapefile")

if __name__ == "__main__":
    main()