TITLE    = 'Popcornered'
PREFIX   = '/video/popcornered'
BASEURL = 'http://popcornered.com/'

ART      = 'art-default.jpg'
ICON     = 'icon-default.png'


# (.?) is useful between text to pull that data

RE_FILM_ID = Regex('films\/\?films=(\d+)"')
RE_DATE = Regex('rates__vote"\>(\d+)\<\/td\>')
RE_COVER = Regex('covers/(.+)\.png')
HTTPCookies = HTTP.CookiesForURL(BASEURL + 'search_results?covers')

###################################################################################################

def Start():

# R stands for Resources folder

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    EpisodeObject.thumb = R(ICON)
    EpisodeObject.art = R(ART)
    MovieObject.thumb = R(ICON)
    MovieObject.art = R(ART)
    
    #HTTP.ClearCookies()
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
    HTTP.Headers['Cookie'] = HTTPCookies
    
###################################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)

# Create main menu.
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(movies, title="Movies: A-Z", url='search_results?a-z'), title="Movies: A-Z", thumb=R(ICON)))
    oc.add(DirectoryObject(key=Callback(movies, title="Movies: Latest Uploads", url='search_results?new'), title="Movies: Latest Uploads", thumb=R(ICON)))
    oc.add(DirectoryObject(key=Callback(movies, title="Movies: Highest Rated", url='search_results?rating'), title="Movies: Highest Rated", thumb=R(ICON)))
    oc.add(DirectoryObject(key=Callback(movies, title="Movies: By Year", url='search_results?year'), title="Movies: By Year", thumb=R(ICON)))
    oc.add(DirectoryObject(key=Callback(movies, title="Movies: Random", url='search_results?random'), title="Movies: Random", thumb=R(ICON)))
    oc.add(DirectoryObject(key=Callback(tvseries, title="TV", url='tv'), title="TV", thumb=R(ICON)))
    #oc.add(DirectoryObject(key=Callback(unfuck, title="Force Clear Cookies"), title="Force Clear Cookies", thumb=R(ICON)))
    return oc

#########################################################################################################################
@route(PREFIX + '/movies', page=int)

def movies(title, url, page=1):

# Create container.
    oc = ObjectContainer(title2=title)

    datecount = 0
    try:
        # Looks like the HTTP.Request requests the page every time the loop runs.
        # Obviously this is not optimal. Need to investigate this.
        # OK, so it is the xpath queries doing the requesting.
        url = BASEURL + url
        filmlist = RE_FILM_ID.findall(HTTP.Request(url).content)
        #Log('this is the list: {}'.format(filmlist))
        HTTPCookies = HTTP.CookiesForURL('http://popcornered.com/search_results?covers')
        HTTP.Headers['Cookie'] = HTTPCookies
        #Log('URL is: {}'.format(url))
        #Log('HTTPCookies is: {}'.format(HTTPCookies))
        #Log('HTTP.Headers[\'Cookie\'] is: {}'.format(HTTP.Headers['Cookie']))
        #Log(HTTP.Request(url).content)
        Log(HTTP.Request('http://popcornered.com/search.php', data='red').content) #testing search just for hell of it.
        for item in filmlist:
            fullurl = BASEURL + 'films/?films=' + item
            Site = HTML.ElementFromURL(fullurl)
            title = Site.xpath("/html/head/title/text()")[0]
            description = Site.xpath('//*[@class="movie__describe"]/text()')[0]
            Log('getmeta: {}'.format(GetMeta(url, datecount)))
            #Log(Site.xpath('//param[contains(@name, "playerID")]')[0].get('value'))
            # Currently only some thumbnails exist in beta site. Try to pull those first.
            thumb = GetThumb(title)
            #Log(HTML.ElementFromURL(url).xpath('//*[@class="movie__images"]/img/@src')[datecount])
            #thumb = originpage.xpath('//*[@class="movie__images"]/img/@src')[datecount]
            #Log('Thumb is: {}'.format(thumb))
            #thumb = BASEURL + thumb
            date = RE_DATE.findall(HTTP.Request(url).content)[datecount]
            date = int(date) #Datetime.ParseDate(date)
            datecount = datecount + 1
            #Log('####### Video Info: #######')
            #Log('Item discovered: {}'.format(item))
            #Log('URL: {}'.format(fullurl))
            #Log('Title: {}'.format(title))
            #Log('Description: {}'.format(description))
            #Log('Thumbnail: {}'.format(thumb))
            #Log('Date: {}'.format(date))
            oc.add(MovieObject(
                url = fullurl,
                title = title,
                summary = description, 
                # Resource.ContentsOfURLWithFallback tests the icon to make sure it is valid or returns the fallback if not
                thumb = thumb, 
                year = date
                ))
    except(IndexError):
        Log('End of the road, Jack.')
        pass
    # This looks like it works to add multiple pages.
    oc.add(NextPageObject(key = Callback(movies, 
        title = str(page + 1),
        url = 'search_results?page=' + str(page + 1),
        page = page + 1),
        title = L('Next Page')
        ))
    # show when a source is empty, count the next page object as 1.
    if len(oc) < 2:
        Log ('ObjectContainer is empty')
        return ObjectContainer(header="Empty", message="No videos found.")      

    return oc

#############################################################################################################################

@route(PREFIX + '/tv')
def tvseries(title, url):
    return ObjectContainer(header="Not Available", message="Unfortunately, TV Series are only available to premium members at this time. Hopefully this will change in the future.")

#############################################################################################################################
# This is a function to pull the thumb from the beta /search_results?covers page
# that didn't work so hot, so now I just try and get lucky with filenames.
# I think maybe the callback above is messing up my thumbnails.
@route(PREFIX + '/getthumb')

def GetThumb(title):
    try:
        title = title.replace(" ","") + '.png'
        thumb = BASEURL +'covers/' + title
        #Log('try 1: {}'.format(thumb))
    except:
        try:
            title = title.strip() + '.png'
            thumb = BASEURL +'covers/' + title
            #Log('try 2: {}'.format(thumb))
        except:
            pass
        thumb = 'http://popcornered.com/video/1.jpg'
    Log('GetThumb is {}'.format(thumb))
    return thumb
    
#############################################################################################################################
@route(PREFIX + '/getmeta')
def GetMeta(url, number):
    metapage = HTML.ElementFromURL(url)
    try:
        description = metapage.xpath('//*[@class="movie movie--preview release"]/div[2]/p[5]/a/text()')[number]
    except:
        description = 'The Ute\'s buggered.'
    return Redirect(description)    
    
