"""This script creates a class to store
information about to a website"""

from urllib.parse import urlparse

from utils import url_utils


class Website:
    """This class stores the information about a website"""

    __LOGO_API = 'https://logo.clearbit.com/'
    __LOGO_SIZE = 24

    def __init__(self, url):
        self.url = url_utils.valid_url(url)
        self.is_valid = True if url else False
        self.domain = urlparse(self.url)[1] if self.is_valid else None
        self.logo_url = '{}{}?size={}'.format(self.__LOGO_API,
                                              self.domain,
                                              self.__LOGO_SIZE) \
            if self.domain else None
        self.contents = None

    def set_contents(self, contents):
        self.contents = contents

    def convert_to_dict(self):
        """This is custom method to convert the Website
         object to dictionary"""

        # It will store dictionary representation of Website object
        formatted_website = dict()

        for key, value in self.__dict__.items():
            if key == 'contents':
                """Using custom object to dict conversion method to convert
                the Contents object to dictionary"""
                formatted_website[key] = value.convert_to_dict()
            else:
                formatted_website[key] = value

        return formatted_website

    def get_title(self):

        content_list = self.contents.content_list
        if not (content_list
                and content_list[0].content_type.name == 'TEXT'
                and content_list[0].type == 'title'):
            return ''

        return content_list[0].text_string
