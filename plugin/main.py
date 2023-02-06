import sys
from urllib.parse import urlencode
from urllib.parse import parse_qsl
from datetime import date, timedelta, datetime
import time
import requests
import json
import locale
locale.setlocale(locale.LC_TIME, "it_IT")

import xbmcgui
import xbmcplugin
import sys

if 'datetime' in sys.modules:
    del sys.modules['datetime']
    
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

VIDEOS = {}
today = str(date.today())
tomorrow = str(date.today() + timedelta(days=1))
today_url = 'https://epg.discovery.indazn.com/eu/v2/Epg?date='+today+'&country=it&languageCode=it&openBrowse=true&timeZoneOffset=60&filters=Sport:289u5typ3vp4ifwh5thalohmq'
tomorrow_url = 'https://epg.discovery.indazn.com/eu/v2/Epg?date='+tomorrow+'&country=it&languageCode=it&openBrowse=true&timeZoneOffset=60&filters=Sport:289u5typ3vp4ifwh5thalohmq'

def get_videos(url, result_filter):
    html_req = requests.get(url).json()
    json_data = json.dumps(html_req)

    y = json.loads(json_data)
    event_str=''
    i=0
    for event in y["Tiles"]:
        if any(text in event["Competition"]["Title"] for text in result_filter) and 'conferenza stampa' not in event['Title']:
            i+=1
            try:
                event_time = datetime.strptime(event['Start'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=1)
            except TypeError:
                event_time = datetime(*(time.strptime(event['Start'], '%Y-%m-%dT%H:%M:%SZ')[0:6])) + timedelta(hours=1)
            event_str+=("{'name': '"+event['Title']+"', 'thumb': "+"'https://image.discovery.indazn.com/eu/v3/eu/none/"+event['Image']['Id']+"/fill/center/top/none/85/1920/1080/jpg/image', 'video': '', 'plot': '''"+event['Label']+"| "+ event_time.strftime("%A %d %b alle %H:%M") +"'''},")
            #print(event["Title"]+", "+event["Start"]+", "+event["Image"]["Id"]+", "+event["Competition"]["Title"])
    if i==0:
        event_str+=("{'name': 'nessun evento per il giorno selezionato', 'thumb': 'https://image.discovery.indazn.com/eu/v3/eu/none/909283909373_image-header_pIt_1661948686000/fill/center/top/none/85/1920/1080/jpg/image', 'video': '', 'plot': ''},")
    return event_str

exec("VIDEOS['Main'] = [" + get_videos(today_url, ["Serie A", "Serie B", 'LaLiga', "UEFA Europa League", "UEFA Europa Conference League"]) + get_videos(tomorrow_url, ["Serie A", "Serie B", 'LaLiga', "UEFA Europa League", "UEFA Europa Conference League"]) + "]")
exec("VIDEOS['Serie C'] = ["+get_videos(today_url,["Serie C"])+get_videos(tomorrow_url,["Serie C"])+"]")
exec("VIDEOS['Femminile'] = ["+get_videos(today_url,["Femminile", "Women", 'Féminine', "Liga F"])+get_videos(tomorrow_url,["Femminile", "Women", 'Féminine', "Liga F"])+"]")

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    return VIDEOS.keys()

def get_videos(category):
    return VIDEOS[category]


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'My Video Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
                          'icon': VIDEOS[category][0]['thumb'],
                          'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category,
                                    'plot': category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = get_videos(category)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': video['name'],
                                    'plot': video['plot'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=video['video'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
