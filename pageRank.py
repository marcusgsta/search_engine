#!/usr/bin/python3
import os
from urllib.parse import unquote



def createLinkIndex(listOfDicts):
    """
    Creates a searcheable index from a list of wikipedia articles.
    Loops through list of files
    and stores a list of dictionaries with
    urls, links and pageRanks (set to inital value of 1.0)
    """
    for page in listOfDicts:
        links = readfile('wikipedia/Links/' + page['url'])
        # if not any(d['links'] == links for d in listOfDicts):
        page['links'] = links
        
        # decode urls
        page['url'] = unquote(page['url'])
    return listOfDicts


# def getUrls(prefix, path):
#     """
#     Gets all filenames in directory (path)
#     """
#     # urls = [prefix + url for url in os.listdir(path)]
#     urls = []
#     for url in os.listdir(path):
#         urls.append(prefix + url)
#         # urls.append(unquote(prefix + url))
#     return urls


def readfile(file):
    links = []
    for link in open(file):
        link = link.strip('\n')
        link = unquote(link)
        links.append(link)
    return links


# Iterate over all pages for a number of iterations
def calculatePageRank(pages):
    """
    @param list with dictionaries

    """
    for page in pages:
        page['url'] = "/wiki/" + page['url']

    MAX_ITERATIONS = 20
    for i in range(MAX_ITERATIONS):
        for page in pages:
            # every page url is checked with all links in all pages
            # to find inbound links
            pr = iteratePR(page['url'], pages)
            page['pageRank'] = pr

    return pages


def iteratePR(url, pages):
    # Calculate page rank value
    pr = 0
    counter = 0
    ls = 0

    # print(url)
    for page in pages:
        if url != page['url']:
            if url in page['links']:
                pr += page['pageRank'] / len(page['links'])
                counter += 1
                ls += len(page['links'])
    # pr = 0.85 * pr + 0.15
    # print(counter)
    # print(ls)
    pr = 0.15 + 0.85 * pr
    return pr
