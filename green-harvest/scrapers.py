import os
import requests
import urllib
from bs4 import BeautifulSoup


class XLSLinksFetcherMixin(object):
    '''Filters the links collected from the index page to only use xls/xlsx files'''

    def filter_links(self, soup_anchors):
        '''filter on xls in filename'''
        soup_anchors = super(XLSLinksFetcherMixin, self).filter_links(soup_anchors)
        return filter(lambda a: "xls" in a.attrs['href'].lower(), soup_anchors)


class PDFLinksFetcherMixin(object):
    '''Filters the links collected from the index page to only use xls/xlsx files'''

    def filter_links(self, soup_anchors):
        '''filter on xls in filename'''
        soup_anchors = super(PDFLinksFetcherMixin, self).filter_links(soup_anchors)
        return filter(lambda a: "pdf" in a.attrs['href'].lower(), soup_anchors)


class Fetcher(object):
    '''Fetches all links on a page'''

    def __init__(self, index_url, download_directory):
        '''Set up index_url and download dir'''
        self.index_url_parse_result = urllib.parse.urlparse(index_url)
        self.index_url = index_url
        self.download_directory = download_directory

    def request_document(self, url):
        '''Generically fetch a url and error on failure'''
        response = requests.get(url)
        response.raise_for_status()
        return response

    def request_index(self):
        '''Fetch the index page'''
        return self.request_document(self.index_url)

    def get_links_from_index(self):
        '''Parses the index page to extract all anchor tags, and return a filtered list'''
        response = self.request_index()
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = self.filter_links(soup.find_all('a'))
        return a_tags

    def filter_links(self, soup_anchors):
        '''Takes a list of BS anchor tags and return only the ones with unique href attributes'''
        new_soup_anchors = []
        seen_links = []
        for anchor in soup_anchors:
            if href not in anchor.attrs:
                if anchor.attrs['href'] not in seen_links:
                    new_soup_anchors.append(anchor)
                seen_links.append(anchor.attrs['href'])
        return new_soup_anchors

    def process_link(self, url):
        '''If the link is relative, we need to rewrite it as a full url'''
        if self.index_url_parse_result.netloc not in url:
            prefix = "%s://%s" % (self.index_url_parse_result.scheme, self.index_url_parse_result.netloc)
            url = prefix + url
        print(url)
        return url

    def handle_file(self, document):
        '''Takes the handle to some content and writes it to a file'''
        filename = document.url.split("/")[-1].replace("%20", "-")
        path = os.path.join(self.download_directory, filename)
        with open(path, "wb") as document_file:
            for block in document.iter_content(1024):
                document_file.write(block)

    def download_documents(self):
        '''
        The core of the process, calls the above method to fill download directory with every file in the linked page
        '''
        links = self.get_links_from_index()
        for link in links:
            link = self.process_link(link.attrs['href'])
            document = self.request_document(link)
            self.handle_file(document)


class ColoradoLicenseFetcher(XLSLinksFetcherMixin, Fetcher):
    '''ColoradoLicenseFetcher'''

    def __init__(self, download_directory):
        super(ColoradoLicenseFetcher, self).__init__(
            "https://www.colorado.gov/pacific/enforcement/med-licensed-facilities",
            download_directory
        )


class WashingtonLicenseFetcher(XLSLinksFetcherMixin, Fetcher):
    '''WashingtonLicenseFetcher'''

    def __init__(self, download_directory):
        super(WashingtonLicenseFetcher, self).__init__(
            "https://lcb.wa.gov/records/frequently-requested-lists",
            download_directory
        )

    def filter_links(self, soup_anchors):
        '''Washington's index also has tobacco and alcohol, we just want weed data'''
        soup_anchors = super(WashingtonLicenseFetcher, self).filter_links(soup_anchors)
        return filter(lambda a: "marijuana" in a.contents[0].lower(), soup_anchors)


class OregonLicenseFetcher(XLSLinksFetcherMixin, Fetcher):
    '''OregonLicenseFetcher'''

    def __init__(self, download_directory):
        super(OregonLicenseFetcher, self).__init__(
            "http://www.oregon.gov/olcc/marijuana/pages/default.aspx",
            download_directory
        )


class CaliforniaLicenseFetcher(PDFLinksFetcherMixin, Fetcher):
    '''CaliforniaLicenseFetcher'''

    def __init__(self, download_directory):
        super(CaliforniaLicenseFetcher, self).__init__(
            "https://www.bcc.ca.gov/clear/license_search.html",
            download_directory
        )


if __name__ == "__main__":
    f = ColoradoLicenseFetcher("colorado")
    f = WashingtonLicenseFetcher("washington")
    f = OregonLicenseFetcher("oregon")
    f = CaliforniaLicenseFetcher("california")
    f.download_documents()
