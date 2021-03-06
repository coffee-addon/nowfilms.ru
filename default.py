#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is a plugin for the site 'nowfilms.ru / kinokong.cc'
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
# [0] - Quality
# [1] - Url to film
# [2] - Url to image
# [3] - Title
# [4] - Positive
# [5] - Negative
def getfilminformations(url):
    # Open url
    req = urllib2.Request(url)
    req.add_header('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/57.0.2987.133 Safari/537.36')
    res = urllib2.urlopen(req)
    html = res.read()
    # First regex to filter image and title
    # Broke into two strings because Python sucks!
    #teststring = '(?:<span class="main-sliders-popup">.*\n.*\n.*\n.*\n.*<b>(.*)<\/b>.*\n.*\n.*\n.*\n.*\n.*)?'
    #teststring = teststring + '<span class="main-sliders-bg">.*\n.*<a href="(.*\.html)".*\n.*\n.*<img src="(.*)" alt="(.*)">'
    #teststring = teststring + '(?:.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n(.*).*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n(.*))?'

    #teststring = '(?:<span class="main-sliders-popup">.*\n.*\n.*\n.*\n.*<b>(.*)<\/b>.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*)?'
    #teststring = teststring + '<span class="main-sliders-bg">.*\n.*<a href="(.*\.html)".*\n.*\n.*<img src="(.*)" alt="(.*)">'
    #teststring = teststring + '(?:(?:.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*|.*\n.*\n.*\n.*\n.*\n.*\n.*)'
    #teststring = teststring + '?<svg viewBox.*\n.*\n.*\n\s+([0-9]+)\s.*\n.*\n.*\n.*\n.*\n.*\n.*\n\s+([0-9]+)\s)?'

    teststring = '(?:<span class="main-sliders-popup">.*\n.*\n.*\n.*\n.*<b>(.*)<\/b>.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*)?'
    #teststring = teststring + '<span class="main-sliders-bg">.*\n.*<a href="(.*\.html)".*\n.*\n.*\n.*<img src="(.*?)" id=".*" alt="(.*?)"'
    teststring = teststring + '<span class="main-sliders-bg">.*\n.*<a href="(.*\.html)".*\n.*\n.*(?:\n.*)?<img src="(.*?)"(?: id=".*")? alt="(.*?)"'
    teststring = teststring + '(?:(?:.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*|.*\n.*\n.*\n.*\n.*\n.*\n.*)'
    teststring = teststring + '?<svg viewBox.*\n.*\n.*\n\s+([0-9]+)\s.*\n.*\n.*\n.*\n.*\n.*\n.*\n\s+([0-9]+)\s)?'

    p = re.compile(teststring)
    UrlsImagesTitles = re.findall(p, html)

    # Create an array and write all found elements to it
    retarr = []
    for (Quality, Url, Image, Title, Positive, Negative) in UrlsImagesTitles:

        if not 'http' in Image:
            tmpImage = "http://kinokong.cc" + Image
            Image = tmpImage

        # Append it to retarr
        tmpArray = []
        tmpArray.append(Image)
        tmpArray.append(Title)
        tmpArray.append(Url)
        tmpArray.append(Quality)
        tmpArray.append(Positive.strip())
        tmpArray.append(Negative.strip())
        retarr.append(tmpArray)

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
    req = urllib2.Request(url)
    req.add_header('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/57.0.2987.133 Safari/537.36')
    res = urllib2.urlopen(req)
    html = res.read()
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
                if imageurl.find("http://") != -1:
                    tmp.append(imageurl)
                else:
                    tmp.append("http://kinokong.cc" + imageurl)
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
    req = urllib2.Request(url)
    req.add_header('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/57.0.2987.133 Safari/537.36')
    req.add_header('Referer', url)
    res = urllib2.urlopen(req)
    html = res.read()

    # Now we can filter url to stream from html response
    # Regex to filter link for single file (e.g. film)
    p1 = re.compile(ur'new.Uppod.*file:"(.*\.[a-z0-9]{1,4})"')
    urltostream_single_url = re.findall(p1, html)

    # Second Regex to filter multiple qualities of single film
    # Example: http://url.mp4,http://secondurl.mp4
    p2 = re.compile(ur'new.Uppod.*file:"(.*?),(http:.*?)"')
    urltostream_multiple_url = re.findall(p2, html)

    # If we found multi quality film, return last(it is probably the best one)
    if urltostream_multiple_url:
        return urltostream_multiple_url[0][len(urltostream_multiple_url)-1]
    # If film has not multi quality return single quality
    elif urltostream_single_url:
        return urltostream_single_url[0]
    else:
        # First search for playlist of the multi file url
        p = re.compile(ur'pl:"(.*).txt"')
        textfileurl = re.findall(p, html)

        if textfileurl:
            textfileurl = textfileurl[0] + '.txt'
            req = urllib2.Request(textfileurl)
            req.add_header('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                         'Chrome/57.0.2987.133 Safari/537.36')
            req.add_header('Referer', url)
            res = urllib2.urlopen(req)
            html = res.read()
            # Regex to filter file number, season and link
            p = re.compile(ur'"comment":"(.*?)","file":"(http:\/\/.*?)"')
            playlist = re.findall(p, html)
            retarr = []
            for (title, url) in playlist:
                if url.find(','):
                    urlArray = url.split(',')
                    for i, myUrl in enumerate(urlArray):
                        tmp = []
                        myTitle = 'Quality ' + str(i+1) + ': ' + title.replace('<br>', ' ')
                        tmp.append(myTitle)
                        tmp.append(myUrl)
                        retarr.append(tmp)
                else:
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

     url = build_url({'mode': 'folder', 'foldername': 'film', 'page': 1})
    li = xbmcgui.ListItem('Films', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'series', 'page': 1})
    li = xbmcgui.ListItem('Serials', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'documentary', 'page': 1})
    li = xbmcgui.ListItem('Shows', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'film/novinki-kinos', 'page': 1})
    li = xbmcgui.ListItem('New', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'cartoons', 'page': 1})
    li = xbmcgui.ListItem('Cartoons', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'animes', 'page': 1})
    li = xbmcgui.ListItem('Anime', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'folder':
    category = args['foldername'][0]
    page = args['page'][0]
    categoryurl = 'http://kinokong.cc/' + category + '/page/' + str(page) + '/'

    # Next page
    nextpage = int(page) + 1
    url = build_url({'mode': 'folder', 'foldername': category, 'page': nextpage})
    li = xbmcgui.ListItem('Next ' + str(nextpage), iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    filminformations = getfilminformations(categoryurl)

    for (element) in filminformations:
        url = build_url({'mode': 'item', 'filmtitle': '[COLOR orange]' + element[3] + '[/COLOR]: [COLOR green]' + element[4] + '[/COLOR] [COLOR red]' + element[5] + '[/COLOR] ' + element[1], 'filmpicture': element[0], 'filmurl': element[2]})
        li = xbmcgui.ListItem('[COLOR orange]' + element[3] + '[/COLOR]: [COLOR green]' + element[4] + '[/COLOR] [COLOR red]' + element[5] + '[/COLOR] ' + element[1].decode('windows-1251'), iconImage=element[0])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)
    xbmc.executebuiltin('Container.SetViewMode(500)')

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
    url = 'http://kinokong.cc/?do=search&subaction=search&story=' + searchtext + '&x=0&y=0'
    filminformations = getfilminformationssearch(url)

    for (element) in filminformations:
        url = build_url({'mode': 'item', 'filmtitle': element[1], 'filmpicture': element[0], 'filmurl': element[2]})
        li = xbmcgui.ListItem(element[1].decode('windows-1251'), iconImage=element[0])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)
