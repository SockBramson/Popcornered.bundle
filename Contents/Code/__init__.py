TITLE    = 'Popcornered'
PREFIX   = '/video/popcornered'
BASEURL = 'http://popcornered.com/'

ART      = 'art-default.jpg'
ICON     = 'icon-default.png'


# (.?) is useful between text to pull that data

RE_FILM_ID = Regex('films\/\?films=(\d+)"')
RE_DATE = Regex('rates__vote"\>(\d+)\<\/td\>')

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

###################################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)

# Create main menu.
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(movies, title="Movies: A-Z", url='search_results?a-z'), title="Movies: A-Z", thumb=R(ICON)))
    oc.add(DirectoryObject(key=Callback(movies, title="Movies: Latest Uploads", url='search_results?new'), title="Movies: Latest Uploads", thumb=R(ICON)))
    oc.add(DirectoryObject(key=Callback(movies, title="Movies: Highest Rated", url='search_results?rating'), title="Movies: Highest Rated", thumb=R(ICON)))
    oc.add(DirectoryObject(key=Callback(tvseries, title="TV", url='tv'), title="TV", thumb=R(ICON)))

    return oc

#########################################################################################################################
@route(PREFIX + '/movies', page=int)

def movies(title, url, page=1):

# Create container.
    oc = ObjectContainer(title2=title)

    datecount = 1
    try:
        # Looks like the HTTP.Request requests the page every time the loop runs.
        # Obviously this is not optimal. Need to investigate this.
        url = BASEURL + url
        filmlist = RE_FILM_ID.findall(HTTP.Request(url).content)
        Log(url)
        for item in filmlist:
            fullurl = BASEURL + 'films/?films=' + item
            title = HTML.ElementFromURL(fullurl).xpath("/html/head/title/text()")[0]
            description = HTML.ElementFromURL(fullurl).xpath("/html/body/div[1]/section/div/div/p/text()")[0]
            # Currently the site has no thumbnails, but I expect this will change.
            thumb = HTML.ElementFromURL(fullurl).xpath('/html/body/div[1]/section/div/div/div[1]/div/iframe/@data-poster')[0]
            thumb = BASEURL + thumb
            date = RE_DATE.findall(HTTP.Request(url).content)[datecount]
            date = int(date) #Datetime.ParseDate(date)
            datecount = datecount + 1
            Log('####### Video Info: #######')
            Log('Item discovered: {}'.format(item))
            Log('URL: {}'.format(fullurl))
            Log('Title: {}'.format(title))
            Log('Description: {}'.format(description))
            Log('Thumbnail: {}'.format(thumb))
            Log('Date: {}'.format(date))
            oc.add(MovieObject(
                url = fullurl,
                title = title,
                summary = description, 
          # Resource.ContentsOfURLWithFallback tests the icon to make sure it is valid or returns the fallback if not
                thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)), 
                year = date
                ))
    except(IndexError):
        Log('End of the road, Jack.')
        pass
# This looks like it works to add multiple pages, however it needs the cookie's 
# "laravel session" in order to remember the sorting.
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
    return ObjectContainer(header="Not Available", message="Unfortunately, TV Series are not available at this time. Hopefully this will change in the future.")

#############################################################################################################################
# This is a function to pull the thumb from a the head of a page
'''
@route(PREFIX + '/getthumb')
def GetThumb(url):
  page = HTML.ElementFromURL(url)
  try:
    thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
    if not thumb.startswith('http://'):
      thumb = http + thumb
  except:
    thumb = R(ICON)
  return thumb
'''
