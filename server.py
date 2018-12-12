#!/usr/bin/python3
from flask import Flask, request, jsonify, render_template, make_response
from flask_restful import Resource, Api
import os
from pageRank import *
from urllib.parse import unquote


app = Flask(__name__, template_folder='templates')
api = Api(app)

# index
pagesWithWordIds = []
# index with links
pagesWithLinks = []
# List of dictionaries for everything
pagesWithDicts = []
# dict for unique word and their id's
wordToId = {}

# Functions to create index

def getIdForWord(word):
    """
    Creates an id for a word,
    and adds to wordToId dictionary
    if not already in it
    """
    if word in wordToId.keys():
        # word found in dictionary
        return wordToId.get(word)
    else:
        # Add word:id to dictionary
        id = len(wordToId)
        wordToId[word] = id
        return id

def createIndex():
    """
    Creates a searcheable index from a list of wikipedia articles.
    ( returns dict like {'url': [list of wordIds]} )
    return list of dicts in format:
    [ {'url': url, 'wordIds': [wordIds], links: []}]
    """
    # get urls
    games_urls = getUrls('Games/', 'wikipedia/Words/Games')
    programming_urls = getUrls('Programming/', 'wikipedia/Words/Programming')
    urls = games_urls + programming_urls
    # Create page objects
    pages = createPages(urls)
    # Convert words to ids and store in dict with unique words 'wordToId'

    pagesDict = []
    for key, value in pages.items():
        listOfIds = []
        for word in value:
            listOfIds.append(getIdForWord(word))

        pagesDict.append( {'url': key,
                            'wordIds': listOfIds,
                            'links': [],
                            'pageRank': 1.0} )
    return pagesDict


def readfile(file):
    words = []
    for line in open(file):
        lineOfWords = line.strip().split(' ')
        words += lineOfWords
    return words


def getUrls(prefix, path):
    """
    Gets all filenames in directory (path)
    """
    # urls = [prefix + url for url in os.listdir(path)]
    urls = []
    for url in os.listdir(path):
        # urls.append(unquote(prefix + url))
        urls.append(prefix + url)
    return urls


def createPages(urls):
    """
    Loops through list of files
    and stores a dictionary with
    page urls mapped to the words in each page
    """
    pages = {}
    for url in urls:
        wordIds = readfile('wikipedia/Words/' + url)
        # if wordIds not in pages.values():
        pages[url] = wordIds
    return pages



# Create index
# in format [ { 'url': url, 'wordIds': wordIds, 'links': [], 'pageRank': 1.0}]
pagesIndex = createIndex()
# Get an array of dicts in format:
# [ {'url' : url, 'links': links, pageRank: 'pageRank'}]
# pagesWithLinks = createLinkIndex()
pagesWithLinks = createLinkIndex(pagesIndex)


for page in pagesWithLinks:
    page['url'] = page['url'].split('/')[1]

# Functions to execute search in index

def getFrequencyScore(wordId, wordIds):
    score = 0
    for id in wordIds:
        if wordId == id:
            score += 1
    return score


def getDocumentLocationScore(queryIds, wordIds):
    score = 0

    for queryId in queryIds:
        if queryId in wordIds:
            score += 1 + wordIds.index(queryId)
        else:
            score += 100000
    return score


def search(query):
    # separate query into list of words
    query = query.lower()
    words = query.split(' ')
    words = [word for word in words if len(word) > 0]

    # Create result dict for pages (and wordids) that contain searched word
    queryIds = [getIdForWord(word) for word in words]

    result = {}

    for page in pagesWithLinks:
        for queryId in queryIds:
            if queryId in page['wordIds']:
                # Only add pages we haven't added before
                if page['url'] not in result:
                    result[page['url']] = page['wordIds']
                    continue
    # if search string not found
    if len(result) == 0:
        return False



    score = {'content': {},
             'location': {},
             'pageRank': {},
             'total': {} }

    # Get Frequency Score
    for page, wordIds in result.items():
        for queryId in queryIds:
            freqScore = getFrequencyScore(queryId, wordIds)
            if freqScore > 0:
                score['content'][page] = freqScore

    # Get document location score
    for page, wordIds in result.items():
        locationScore = getDocumentLocationScore(queryIds, wordIds)
        score['location'][page] = locationScore

    # Get all page ranks
    pageRanks = calculatePageRank(pagesWithLinks)

    # Convert/clean urls
    for p in pageRanks:
        print(p['url'])
        p['url'] = p['url'].split('/wiki/')[1]


    # Get page ranks for result
    for page, wordIds in result.items():
        for p in pageRanks:
            if page == p['url']:
                score['pageRank'][page] = p['pageRank']
                break

    score['pageRank'] = normalize(score['pageRank'], False)
    score['location'] = normalize(score['location'], True)
    score['content'] = normalize(score['content'], False)

    # Generate result list
    resultList = []
    for page, contentScore in score['content'].items():
        total = round(contentScore +
                    0.5 * score['pageRank'][page] +
                    0.8 * score['location'][page], 2)

        resultList.append({
        'url': page,
        'total': total,
        'content': round(contentScore, 2),
        'location': round(0.8 * score['location'][page], 2),
        'pageRank': round(0.5 * score['pageRank'][page], 2)
        })

    resultList = sorted(resultList, key=lambda x: x['total'], reverse=True)

    return resultList[:5]


def normalize(scores, smallIsBetter):
    """
    Scales values between 0 and 1
    """
    if smallIsBetter:
        # Invert smaller values to higher values
        # and scale between 0 and 1
        # Find min value in the array
        minimum = min(scores.values())
        # Divide min value by score
        # avoid division by zero
        normalized_scores = {}
        for page, score in scores.items():
            normalized_scores[page] = minimum / max(score, 0.00001)
        return normalized_scores
    else:
        # Scale higher values between 0 and 1
        # Find max value in array
        maximum = max(scores.values())
        # Divide all scores by max value
        normalized_scores = {}
        for page, score in scores.items():
                normalized_scores[page] = score / maximum
        return normalized_scores


# Routes

class About(Resource):
    """
    Welcome route
    """
    def get(self):
        headers = {'Content-Type': 'text/html'}

        return make_response(render_template('about.html'), 200, headers)


class SearchEngine(Resource):
    """
    Renders page with search form
    """
    def get(self):
        headers = {'Content-Type': 'text/html'}

        return make_response(render_template('search_engine.html'), 200, headers)


class SearchResult(Resource):
    """
    Search Engine route
    Takes a search query
    """
    def get(self):
        headers = {'Content-Type': 'text/html'}
        query = request.args.get('query')

        if len(query) > 0:
            result = search(query)
        else: result = "empty"


        return make_response(render_template('search_engine.html', result=result, word=query), 200, headers)


# Routes
api.add_resource(SearchEngine, '/') # Route
api.add_resource(SearchResult, '/search/') # Route
api.add_resource(About, '/about') # Route


if __name__ == '__main__':
     app.run()
