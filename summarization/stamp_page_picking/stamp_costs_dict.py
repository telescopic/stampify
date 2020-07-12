''' Module to define and return the stamp costs dict '''

from data_models.summarizer_output import StampPageType

stamp_costs_dict = dict()

stamp_costs_dict[StampPageType.TEXT_ONLY.name] = 1.0
stamp_costs_dict[StampPageType.QUOTED.name] = 2.5
stamp_costs_dict[StampPageType.EMBEDDED.name] = 5.0
stamp_costs_dict[StampPageType.MEDIA_ONLY.name] = 7.5
stamp_costs_dict[StampPageType.MEDIA_WITH_TEXT.name] = 10.0
stamp_costs_dict[StampPageType.MEDIA_WITH_TEXT_AND_TITLE.name] = 20.0


def fetch_stamp_costs_dict():
    return stamp_costs_dict
