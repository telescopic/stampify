''' Module to define and return the stamp costs dict '''

from data_models.summarizer_output import StampPageType

STAMP_COSTS_DICT = dict()

STAMP_COSTS_DICT[StampPageType.TEXT_ONLY.name] = 1.0
STAMP_COSTS_DICT[StampPageType.QUOTED.name] = 2.5
STAMP_COSTS_DICT[StampPageType.EMBEDDED.name] = 5.0
STAMP_COSTS_DICT[StampPageType.MEDIA_ONLY.name] = 7.5
STAMP_COSTS_DICT[StampPageType.MEDIA_WITH_TEXT.name] = 10.0
STAMP_COSTS_DICT[StampPageType.MEDIA_WITH_TEXT_AND_TITLE.name] = 20.0


def get_stamp_page_costs():
    return STAMP_COSTS_DICT
