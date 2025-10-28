from collections import Counter
import re
import sys
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup

wordFrequencies = dict()

def scraper(url, resp):
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    text = soup.get_text()
    updateWordFrequencies(tokenize(text))
    writeFrequencies("frequencies.txt", 50)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        return list()
    links = []
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        href = urldefrag(href)[0]  
        if href not in links and href != url:
            links.append(href)
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.hostname not in ("ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def tokenize(text):
    tokens = []
    word = ''
    for letter in text:
        if (letter.isascii() and letter.isalnum()):
            word += letter.lower()
        else:
            if len(word):
                tokens.append(word)
                word = ''
    if len(word):
        tokens.append(word)
    return tokens


def updateWordFrequencies(tokens):
    for token in tokens:
        if isStopWord(token):
            continue
        if token in wordFrequencies:
            wordFrequencies[token] += 1
        else:
            wordFrequencies[token] = 1
    return wordFrequencies

def writeFrequencies(file, n=-1):
    with open(file, "w", encoding="utf-8") as sys.stdout:
        printFrequencies(wordFrequencies, n)


def printFrequencies(frequencies, n=-1):
    frequencies = dict(sorted(frequencies.items(), key=lambda item: item[1], reverse=True))
    for key, value in frequencies.items():
        print(f"{key} {value}")
        n -= 1
        if n == 0:
            break

def isStopWord(word):
    stopWords = {'some', 'not', "we've", 'few', 'hers', 'should', "we're", 'was', 'ought', "they're", 'herself', "i'll", 'she', "she'd", 'do', 'in', 'himself', 'off', "here's", 'which', 'of', 'my', 'we', "don't", 'because', 'or', 'the', 'other', "there's", 'own', 'what', 'both', 'with', 'themselves', 'myself', 'all', 'into', "doesn't", "it's", "how's", 'once', 'between', 'by', 'down', "you'll", 'been', 'that', 'same', 'our', 'whom', 'ours', "they'll", 'am', "isn't", 'to', 'his', 'when', "aren't", 'cannot', 'very', 'her', 'you', 'have', 'most', 'if', 'a', 'are', 'it', 'how', 'did', "let's", 'at', 'does', "can't", 'has', 'here', "didn't", "they've", 'before', 'until', 'under', 'and', 'as', 'why', 'could', 'through', 'so', 'me', 'again', 'ourselves', "he's", "where's", "weren't", 'them', 'further', 'but', 'more', 'i', 'for', 'theirs', 'be', 'this', "she'll", 'your', "he'll", "you're", "shouldn't", 'is', "haven't", "i'm", "i've", 'him', 'no', 'being', 'those', 'on', 'below', 'then', 'were', "you've", "you'd", 'nor', 'doing', "we'd", "she's", "that's", 'itself', 'while', 'such', "when's", "shan't", 'too', "what's", 'during', 'who', 'yourself', 'against', "i'd", 'above', 'after', "mustn't", 'there', 'about', 'yours', 'from', 'over', 'out', 'any', 'they', "won't", 'each', 'up', "hasn't", 'only', 'an', "couldn't", "he'd", 'where', 'having', "wouldn't", 'yourselves', "who's", 'its', 'their', "wasn't", 'had', "they'd", 'would', "why's", 'he', 'than', "hadn't", "we'll", 'these'}
    return word in stopWords