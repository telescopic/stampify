''' Module to define and return the stamp costs dict '''

from data_models.summarizer_output import StampPageType

STAMP_SCORES = dict()

STAMP_SCORES[StampPageType.TEXT_ONLY.name] = 1.0
STAMP_SCORES[StampPageType.QUOTED.name] = 2.5
STAMP_SCORES[StampPageType.EMBEDDED.name] = 5.0
STAMP_SCORES[StampPageType.MEDIA_ONLY.name] = 7.5
STAMP_SCORES[StampPageType.MEDIA_WITH_TEXT.name] = 10.0
STAMP_SCORES[StampPageType.MEDIA_WITH_TEXT_AND_TITLE.name] = 20.0


def get_stamp_page_score(stamp_page):
    ''' returns the stamp score from the dict'''
    return STAMP_SCORES[stamp_page.stamp_type.name]
