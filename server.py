#!/usr/bin/python3
from flask import Flask, request, jsonify, render_template, make_response
from flask_restful import Resource, Api
import os
from pageRank import *
from math import ceil
from urllib.parse import unquote


app = Flask(__name__, template_folder='templates')
api = Api(app)

# index
# pagesWithWordIds = []
# index with links
pagesWithLinks = []
# List of dictionaries for everything
# pagesWithDicts = []
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

    pages = createPages(urls)

    return pages


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
    urls = []
    for url in os.listdir(path):
        urls.append(prefix + url)
    return urls


def createPages(urls):
    """
    Loops through list of files
    and stores a dictionary of dictionaries, where
    'url' : {}
    wordIds, empty list of links and pageRank start value
    """
    pages = {}
    for url in urls:
        words = readfile('wikipedia/Words/' + url)
        wordIds = []
        for word in words:
            wordIds.append(getIdForWord(word))

        pages[url] = {
                'wordIds': wordIds,
                'links': [],
                'pageRank': 1.0
                }
    return pages


# Create index dict of dicts: {'url': { } }
pagesIndex = createIndex()
pagesWithLinks = createLinkIndex(pagesIndex)
pageRanks = calculatePageRank(pagesWithLinks)


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

    for url, dict in pagesIndex.items():
    # for page in pageRanks:
        for queryId in queryIds:
            if queryId in dict['wordIds']:
            # if queryId in page['wordIds']:
                # Only add pages we haven't added before
                # if url not in result:
                result[url] = dict['wordIds']
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

    # Get page ranks for result
    for page, wordIds in result.items():
        for url, dict in pageRanks.items():
            if page == url:
                score['pageRank'][page] = dict['pageRank']
                break

    score['pageRank'] = normalize(score['pageRank'], False, True)
    score['location'] = normalize(score['location'], True)
    score['content'] = normalize(score['content'], False)

    # Generate result list
    resultList = []
    for page, contentScore in score['content'].items():
        total = round(contentScore +
                    0.5 * score['pageRank'][page] +
                    0.8 * score['location'][page], 3)

        resultList.append({
        'url': page,
        'total': total,
        'content': round(contentScore, 3),
        'location': round(0.8 * score['location'][page], 3),
        'pageRank': round(0.5 * score['pageRank'][page], 3),
        'cleanUrl': unquote(page)
        })

    resultList = sorted(resultList, key=lambda x: x['total'], reverse=True)


    return resultList[:5]


def normalize(scores, smallIsBetter, isPageRank=False):
    """
    Scales values between 0 and 1
    """
    if smallIsBetter:
        # Invert smaller values to higher values
        # and scale between 0 and 1
        # Find min value in the array
        if isPageRank:
            minimum = min(d['pageRank'] for d in pageRanks.values())
        else:
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
        if isPageRank:
            maximum = max(d['pageRank'] for d in pageRanks.values())
        else:
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
     app.run(port:5001)
