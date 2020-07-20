"""This script creates Stampifier which pipelines all internal modules"""

import logging

from classification.classifier import Classifier
from data_models.stampifier_output import StampifierOutput
from data_models.website import Website
from error.stampifier_error import InvalidUrlError
from extraction.extractor import Extractor
from stamp_generation.stamp_generator import StampGenerator
from summarization.extractor_output_preprocessor import \
    ExtractorOutputPreprocessor
from summarization.summarizer import Summarizer

LOGGER = logging.getLogger(__name__)


class Stampifier:
    """Creates class for stampification"""

    def __init__(self, url, max_pages, enable_animations):
        self.url = url
        self.max_pages = max_pages
        self._website = Website(self.url)
        self.is_stampifiable = False
        self.stampified_pages = None
        self.enable_animations = enable_animations

    def stampify(self):
        """Starts the stampification process"""

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename='website.log',
                            level=logging.DEBUG)

        if not self._website.is_valid:
            raise InvalidUrlError()

        return self.__convert_website_to_stamp()

    def __convert_website_to_stamp(self):
        """This method is the pipeline between all the modules"""

        _extractor = Extractor(self._website.url)
        self._website.set_contents(_extractor.extract_html())

        LOGGER.debug(self._website.convert_to_dict())

        stampified_pages = self.get_stampified_content()

        generated_stamp \
            = StampGenerator(self._website,
<<<<<<< HEAD
                             _classifier_and_summarizer_response[
                                 "stamp_pages"],
                             self.enable_animations).stamp_html
=======
                             stampified_pages
                             ).stamp_html
>>>>>>> Code restructure to make classifier throw WebsiteNotStampifiableError

        LOGGER.debug(generated_stamp)

        return StampifierOutput(generated_stamp,
                                self._website.get_title())

    def _preprocess_contents(self):
        '''
        This method will use ExtractorOutputPreprocessor
        to split the contents into different types
        '''
        output_preprocessor \
            = ExtractorOutputPreprocessor(self._website.contents)
        self.preprocessed_contents \
            = output_preprocessor.get_preprocessed_content()

    def get_stampified_content(self):
        ''' returns the list of stamp pages'''
        # pre-process the contents first
        self._preprocess_contents()

        # classify the page as stampifiable or not
        self._classify()

        # summarize
        self._summarize()

        # order the stamp pages
        self._order_stamp_pages()

        return self.stampified_pages

    def _classify(self):
        classifier = Classifier(
            self.preprocessed_contents,
            max_pages=self.max_pages,
            webpage_title=self._website.get_title()
        )
        classifier.is_page_stampifiable()
        self.webpage_topic_is_plural = classifier.is_webpage_topic_plural()

    def _summarize(self):
        summarizer = Summarizer(
            self.preprocessed_contents,
            self.max_pages,
            self.webpage_topic_is_plural
        )

        self.stampified_pages = summarizer.get_summarized_content()

    def _get_min_index_for_stamp_page(self, stamp_page):
        if stamp_page.para_index != -1:
            return stamp_page.get_weighted_text_index()

        if stamp_page.media_index != -1:
            return stamp_page.media_index

    def _order_stamp_pages(self):
        # separate this as function so
        # logic can be amended to include
        # more information if necessary
        self.stampified_pages.stamp_pages.sort(
            key=self._get_min_index_for_stamp_page)
