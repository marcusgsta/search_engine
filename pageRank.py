#!/usr/bin/python3
import os
from urllib.parse import unquote

def createLinkIndex(dictOfDicts):
    """
    Creates a searchable index from a list of wikipedia articles.
    Loops through list of files
    and stores a dict of dictionaries with
    urls, links and pageRanks (set to inital value of 1.0)
    """
    for url, dict in dictOfDicts.items():
        links = readfile('wikipedia/Links/' + url)
        dict['links'] = links

    return dictOfDicts


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
    @param dict of dictionaries
    """

    MAX_ITERATIONS = 20
    for i in range(MAX_ITERATIONS):
        for url, dict in pages.items():
            # every page url is checked with all links in all pages
            # to find inbound links
            pr = iteratePR(url, pages)
            dict['pageRank'] = pr
    return pages


def iteratePR(this_url, pages):
    # Calculate page rank value
    pr = 0
    for url, dict in pages.items():
        # if url != this_url:
        link_url = "/wiki/" + unquote(this_url).split('/')[1]
        if link_url in dict['links']:
            pr += dict['pageRank'] / len(dict['links'])
            # pr += 0.85 * dict['pageRank'] / len(dict['links'])
    return 0.85 * pr + 0.15
