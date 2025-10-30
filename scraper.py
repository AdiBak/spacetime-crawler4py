from contextlib import redirect_stdout
import re
import hashlib
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
from utils import get_logger
from utils.response import Response


seen_text_hashes = set()
seen_urls = set()
wordFrequencies = dict()
longestPage = 0
logger = get_logger("scraper")

def scraper(url, resp):
    seen_urls.add(url)
    writeUniquePageCounter("unique_pages.txt")

    links = extract_next_links(url, resp)
    valid_links = [link for link in links if is_valid(link)]
    return valid_links



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

     if resp.status is None or resp.status < 200 or resp.status >= 400:
        return []

     if not resp.raw_response or not resp.raw_response.content:
        return []

     if len(resp.raw_response.content) > 5_000_000:
        return []

     soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

     text = soup.get_text(separator=' ', strip=True)
     words = text.split()

     tokenized = tokenize(text)
     updateWordFrequencies(tokenized)
     writeFrequencies("frequencies.txt", -1)
     global longestPage

    
     if len(tokenized) > longestPage:
        longestPage = len(tokenized)
        writeLongestPageLength("longest_page.txt", url, longestPage, text)


     if len(words) < 50:
        return []

     text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
     if text_hash in seen_text_hashes:
        return []
     seen_text_hashes.add(text_hash)
     
     links = set()
     for tag in soup.find_all('a', href=True):
        new_url = urljoin(url, tag['href'])
        new_url = urldefrag(new_url)[0]  
        if not new_url in seen_urls:
            links.add(new_url)

     return list(links)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
     try:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        if not parsed.hostname or not parsed.hostname.endswith(
            ("ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu")
        ):
            return False

        if any(sub in parsed.netloc for sub in [
            "wics.ics.uci.edu", 
            "ngs.ics.uci.edu",
        ]):
            return False

        if re.search(r"(calendar|ical|tribe|event|events|feed|share|login|signup|~eppstein/pix)", parsed.path.lower()):
            return False

        if parsed.query and parsed.query.count('=') > 5:
            return False

        # if len(url) > 200:
        #     return False

        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$",
            parsed.path.lower(),
        ):
            return False

        return True

     except Exception:
        print("Error for ", url)
        raise


def tokenize(text):
    tokens = []
    word = ''
    for i, letter in enumerate(text):
        if (letter.isascii() and letter.isalnum()) or (letter == "'" or letter == "-" or letter == "’"):
            word += letter.lower()
        elif (letter == "." and i < len(text) - 1 and text[i + 1] != " "):
            word += letter
        else:
            if len(word):
                for letter in word:
                    if letter.isalnum():
                        tokens.append(word)
                        break
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
    with open(file, "w", encoding="utf-8") as f:
        with redirect_stdout(f):
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


def writeUniquePageCounter(file):
    with open(file, "w", encoding="utf-8") as f:
        with redirect_stdout(f):
            print(len(seen_urls))

def writeLongestPageLength(file, url, longestPage, text):
    with open(file, "w", encoding="utf-8") as f:
        with redirect_stdout(f):
            print(f"url: {url}\nnumber of words: {longestPage}\n{text}")