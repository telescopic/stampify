''' module to define the web-page stampifiable Classifier'''


class Classifier:
    '''Class to determine if a webpage is stampable

    Detemines if a webpage is stampable based on the following
    max(media_count,text_count) + embedded_content_count >= min_pages
    '''

    def __init__(
            self,
            contents,
            max_pages):
        self.contents = contents
        # max pages is maximum number of stamp pages allowed
        # min pages is the minimum number of stamp pages
        # required
        self.min_pages = max_pages // 2

    def classify(self):
        ''' classifies the web page as stampifiable or not
        and sets the is_stampifiable attribute accordingly
        '''
        # max is picked since some unused media/sentences
        # might still be used for stamp page contents
        self.is_stampifiable \
            = max(
                max(
                    self.contents.get_normal_text_content_count(),
                    self.contents.get_title_text_content_count()
                ),
                self.contents.get_media_content_count()
            ) \
            + self.contents.get_embedded_content_count() \
            + self.contents.get_quoted_content_count() >= self.min_pages

    def is_page_stampifiable(self):
        ''' returns the is_stampifiable flag'''
        self.classify()
        return self.is_stampifiable
