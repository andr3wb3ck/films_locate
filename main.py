import time
import folium
from geopy.geocoders import Nominatim
from geopy import distance


def get_film_locations(input_year):
    """
    Function reads data from location.list file
    :param input_year: string
    :return: set
    """
    film_set = set()
    with open('data/locations.csv', 'r', encoding="utf-8", errors='ignore') as file:
        line = file.readline()
        while line:
            if line.split(',')[1] == input_year and line.split(',')[1] != 'NO DATA':
                film_set.add(tuple([line.split(',')[0].strip(), line.split(',')[-1].strip()]))
            line = file.readline()
    return film_set


def get_location_coordinates(films_set, film_number=0):
    """
    Function to get coordinates of given films
    :param films_set: set
    :param film_number: int
    :return: list
    """
    if not film_number:
        film_number = len(films_set)

    films_list = sorted(list(films_set))
    print(f'List has {len(films_list)} films with specified year. '
          f'\nAmount of films to analyze: {film_number} '
          f'\n------------------------------')

    locations_loss = 0
    lost_locations = []
    output_list = []
    coordinates_set = set()
    geoloc = Nominatim(user_agent="map")
    print('Loading...')
    for i in range(film_number):
        if '.' in films_list[i][-1]:
            geo_value = geoloc.geocode(films_list[i][-1]
                                       [films_list[i][-1].find('.'):], timeout=30)
        else:
            geo_value = geoloc.geocode(films_list[i][-1], timeout=30)
        if geo_value is None or \
                (geo_value.latitude, geo_value.longitude) in coordinates_set:
            locations_loss += 1
            lost_locations.append(films_list[i])
            continue
        time.sleep(1.1)
        coordinates = (geo_value.latitude, geo_value.longitude)
        coordinates_set.add(coordinates)
        output_list.append([films_list[i][0], coordinates])
    print(f"Lost {locations_loss} locations overall, due to geopy", lost_locations)
    return output_list


def get_nearest_films(films_list, number, input_location):
    """
    Function finds the nearest films near user specified location
    :param input_location: list
    :param films_list: list
    :param number: int
    :return: list
    """
    output_list = []
    for film_data in films_list:
        film_dist = int(distance.distance(film_data[1], input_location).km)
        film_data.append(film_dist)
        output_list.append(film_data)
        output_list.sort(key=lambda x: x[-1])
        if len(output_list) >= int(number):
            output_list.pop()
    dist_list = [film[-1] for film in output_list]
    print(f'Closest film distance: {dist_list[0]} km.')
    print(f'Furthest film distance: {dist_list[-1]} km.')
    return output_list


def get_html_file(films_list, input_location):
    """
    Function generates html file with map
    :param input_location: list
    :param films_list: list
    :return: None
    """
    geo_map = folium.Map(
        location=[48.8589507, 2.2770201],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    for each in films_list:
        folium.Marker(each[1], popup=f'<i>{each[0]}</i>',
                      tooltip=str(each[2]) + 'km. to user location').add_to(geo_map)
    folium.Marker(input_location, popup=f'<i>User location</i>',
                  icon=folium.Icon(color='red', icon='info-sign')).add_to(geo_map)
    folium.TileLayer('stamentoner').add_to(geo_map)
    fg_pp = folium.FeatureGroup(name="Population")
    fg_pp.add_to(geo_map)
    fg_pp.add_child(
        folium.GeoJson(data=open('data/world.json', 'r',
                                 encoding='utf-8-sig').read(),
                       style_function=lambda x: {'fillColor': 'yellow' if
                       x['properties']['POP2005'] < 10000000 else 'pink' if
                       10000000 <= x['properties']['POP2005'] < 20000000 else 'purple'}))
    folium.LayerControl().add_to(geo_map)
    geo_map.save('index.html')


user_year = input('Enter a year: ')
user_film_analyze_num = int(input('Enter number of films: '))
user_markers_num = int(input('Enter number of nearest film markers: '))
user_location = input('Enter specified locaiton: (ex. "lat, lon"): ').split(',')

film_name_location = get_film_locations(user_year)
data_list = get_location_coordinates(film_name_location,
                                     film_number=user_film_analyze_num)
data_list = get_nearest_films(data_list, user_markers_num, user_location)
get_html_file(data_list, user_location)
