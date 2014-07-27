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

#################################################################################################################
@route(PREFIX + '/movies/new', page=int)
def MLatest(title, url):


# The parsing API is followed by .xpath(‘//PARENTELEMENT’): where PARENTELEMENT is the parent element within the XML document for  
# which you want to return data values to the variables for the videos. For example each video in your RSS feed may be contained 
# within an Item element tag that has element tags for title, thumbnail, description, etc.

# Open the object container
    oc = ObjectContainer(title2=title)

# The HTML.ElementFromURL create a tree structure of all the elements, attributes and data in your html documents called a DOM Tree. 
# This tree structure is necessary to pull data with xpath commands
    html = HTML.ElementFromURL(url)

# We start a for loop for all the items we want to pull off of the page.    You will need to search the source document and play around with
# and xpath checker to find the right structure to get you to a point of returning the full list of items you want to pull the data from.
    for video in html.xpath('//div/div/div/ul/li/ul/li'):
  # need to check if urls need additions and if image needs any additions to address
        url = video.xpath('./div/a//@href')[0]
        # here we are adding the sites domain name with a global variable we set at the start of the channel
        url = WebsiteURL + url
        thumb = video.xpath('./div/a/img//@style')[0]
        # A value that is returned may have extra code around it that needs to be removed. Here we use the replace string method to fix the thumb address
        thumb = thumb.replace("background-image:url('", '').replace("');", '')
        title = video.xpath('./div/div/p/a//text()')[0]

# SEE THE LINKS AT THE TOP FOR MORE DETAILED INFO ON XPATH 
# We are using xpath to get of all the values for each element with the parent element returned by the variable video 
# the syntax is: video.xpath (‘./CHILDELEMENT’)[FIRSTVALUE].FORMAT or video.xpath (‘./CHILDELEMENT/FORMAT’)[FIRSTVALUE]
# where CHILDELEMENT is the xpath commands that gets us to the location of the data in the child element ( ex. title, url, date),
# FIRSTVALUE is the first occurrence of the child element. Usually you want to get all occurences of the child element for 
# each parent element so we give this a value of [0] (Python starts the count at zero), and FORMAT defines whether we want 
# to return the data contained in the element as text or as an attribute.  The syntax is are .text or .get(‘ATTRIBUTE’) 
# or //text() and //@ATTRIBUTE when attached to the child element xpath where ATTRIBUTE is the name of the attribute 
# you want to return ex. //@href or .get(href) to return the anchor attribute href="www.domainname.com/file.htm"

# this is where the values for each child element we specified are added to the channel as video clip objects the naming scheme for
# the values passed here are listed in the Framework Documentation for attributes of VideoClipObjects

        oc.add(VideoClipObject(
            url = url, 
            title = title, 
            thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))))
      
# This code below is helpful to show when a source is empty
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")      
          
# it will loop through and return the values for all items in the page 
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
