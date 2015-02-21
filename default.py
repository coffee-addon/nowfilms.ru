#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is a plugin for the site 'nowfilms.ru'
# It was written by coffee
#
# Simple and performant plugin to look films etc... It was tested on Raspberry Pi 2 + Openelec + Kodi 14.1
#
# Copyright (C) 2015 coffee
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
# Regex
import re

# HTTP operations
import urllib2
import pprint

# Types, to check if variable is of type
import types

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


mode = args.get('mode', None)

# Gets film informations
#
# Returns array with following informations:
# Array:
# [0] - Imageurl
# [1] - Title
# [2] - Url to film
def getfilminformations(url):
    # Open url
    response = urllib2.urlopen(url)
    html = response.read()
    # First regex to filter image and title
    # p = re.compile(ur'<span class="new_movie4 oops" style="background: url\((.*)\)\ no-repeat.*alt="(.*)"')
    p = re.compile(ur'<span class="new_movie4.*".*<img src="(.*)" alt="(.*)"')
    imagesandtitles = re.findall(p, html)
    # Second regex to filter url to film
    p = re.compile(ur'<span class="new_movie[6|8]"><a href="(.*)">(.*)<\/a>\s{1,4}<\/span>')
    urlstofilm = re.findall(p, html)
    # Remove duplicates
    urlstofilm = list(set(urlstofilm))
    # Create an array and write all found elements to it
    retarr = []
    for (imageurl, title) in imagesandtitles:
        for (url, secondtitle) in urlstofilm:
            if title == secondtitle:
                tmp = []
                tmp.append('http://nowfilms.ru'+imageurl)
                tmp.append(title)
                tmp.append(url)
                retarr.append(tmp)

    return retarr

# Gets film informations, but after a search
# another method because of very different regex
# to keep code clean
#
# Returns array with following informations:
# Array:
# [0] - Imageurl
# [1] - Title
# [2] - Url to film
def getfilminformationssearch(url):
    # Open url
    response = urllib2.urlopen(url)
    html = response.read()
    # First regex to filter image and title
    # p = re.compile(ur'<span class="new_movie4 oops" style="background: url\((.*)\)\ no-repeat.*alt="(.*)"')
    p = re.compile(ur'<span class="new_movie4.*".*<img src="(.*)" alt="(.*)"')
    imagesandtitles = re.findall(p, html)
    # Second regex to filter url to film
    p = re.compile(ur'<h2 class="new_movie6"><a href="(.*)"><b>(.*)<\/b><\/a> <\/h2>')
    urlstofilm = re.findall(p, html)
    # Remove duplicates
    urlstofilm = list(set(urlstofilm))
    # Create an array and write all found elements to it
    retarr = []
    for (imageurl, title) in imagesandtitles:
        for (url, secondtitle) in urlstofilm:
            if title == secondtitle:
                tmp = []
                tmp.append('http://nowfilms.ru'+imageurl)
                tmp.append(title)
                tmp.append(url)
                retarr.append(tmp)

    return retarr



# Gets url to stream
#
# Returns string|array
# If array:
# [0] - Title of the series
# [1] - Url to serie
def getfilmurltostream(url):
    # Get Url to stream
    # First open the link to the film
    response = urllib2.urlopen(url)
    html = response.read()

    # Now we can filter url to stream from html response
    # Regex to filter link for single file (e.g. film)
    p = re.compile(ur'new.Uppod.*file:"(.*)",')
    urltostream = re.findall(p, html)

    if urltostream:
        return urltostream[0]
    else:
        # First search for playlist of the multi file url
        p = re.compile(ur'pl:"(.*).txt"')
        textfileurl = re.findall(p, html)

        if textfileurl:
            textfileurl = textfileurl[0] + '.txt'
            response = urllib2.urlopen(textfileurl)
            html = response.read()
            # Regex to filter file number, season and link
            p = re.compile(ur'"comment":"(.*)","file":"(.*)"')
            playlist = re.findall(p, html)
            retarr = []
            for (title, url) in playlist:
                tmp = []
                tmp.append(title.replace('<br>', ' '))
                tmp.append(url)
                retarr.append(tmp)

            return retarr
        else:
            return []

if mode is None:
    url = build_url({'mode': 'search'})
    li = xbmcgui.ListItem('Search', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'films', 'page': 1})
    li = xbmcgui.ListItem('Films', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'serial', 'page': 1})
    li = xbmcgui.ListItem('Serials', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'dokumentalnyy', 'page': 1})
    li = xbmcgui.ListItem('Shows', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'novinki', 'page': 1})
    li = xbmcgui.ListItem('New', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'multfilm', 'page': 1})
    li = xbmcgui.ListItem('Cartoons', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'anime', 'page': 1})
    li = xbmcgui.ListItem('Anime', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'folder':
    category = args['foldername'][0]
    page = args['page'][0]
    categoryurl = 'http://nowfilms.ru/' + category + '/page/' + str(page) + '/'

    # Next page
    nextpage = int(page) + 1
    url = build_url({'mode': 'folder', 'foldername': category, 'page': nextpage})
    li = xbmcgui.ListItem('Next ' + str(nextpage), iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    filminformations = getfilminformations(categoryurl)

    for (element) in filminformations:
        url = build_url({'mode': 'item', 'filmtitle': element[1], 'filmpicture': element[0], 'filmurl': element[2]})
        li = xbmcgui.ListItem(element[1].decode('windows-1251'), iconImage=element[0])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'item':
    filmtitle = args['filmtitle'][0].decode('windows-1251')
    filmpicture = args['filmpicture'][0]
    filmurl = args['filmurl'][0]
    streamurl = getfilmurltostream(filmurl)
    # Now we have to decide
    # Is it a single film or a serial?
    if isinstance(streamurl, types.StringTypes):
        # We found a film url
        li = xbmcgui.ListItem(filmtitle, iconImage=filmpicture)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamurl, listitem=li)
        xbmcplugin.endOfDirectory(addon_handle)
    else:
        # We found a serial array
        for (title, url) in streamurl:
            li = xbmcgui.ListItem(title, iconImage=filmpicture)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

        xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'search':
    keyboard = xbmc.Keyboard('', 'Search')
    keyboard.doModal()
    searchtext = ''
    if keyboard.isConfirmed():
        searchtext = keyboard.getText()

    searchtext = searchtext.decode('utf-8').encode('windows-1251')
    url = 'http://nowfilms.ru/?do=search&subaction=search&story=' + searchtext + '&x=0&y=0'
    filminformations = getfilminformationssearch(url)

    for (element) in filminformations:
        url = build_url({'mode': 'item', 'filmtitle': element[1], 'filmpicture': element[0], 'filmurl': element[2]})
        li = xbmcgui.ListItem(element[1].decode('windows-1251'), iconImage=element[0])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)