import json
from unittest.mock import Mock, patch

import pytest

from summarization.bad_request_error import BadRequestError
from summarization.image_caption_detection import ImageCaptionDetector


def mocked_requests_post(*args, **kwargs):
    json_data = json.loads(kwargs["data"])
    response_dict = {}
    status_code = 200
    if json_data["requests"][0]["image"]["source"]["imageUri"] \
            == "img_url_with_caption":
        response_dict["textAnnotations"] = {}

    elif json_data["requests"][0]["image"]["source"]["imageUri"] \
            == "img_url_without_caption":
        # don't modify the dict
        pass
    else:
        status_code = 400

    response = json.dumps({
        "responses": [
            response_dict
        ]
    })
    return Mock(status_code=status_code, content=response)


@patch(
    "summarization.image_caption_detection.requests.post",
    side_effect=mocked_requests_post)
def test_request_format(mocked_post):
    image_caption_detector = ImageCaptionDetector()
    formatted_request = image_caption_detector._format_single_request("url")

    assert isinstance(formatted_request, dict)

    assert "image" in formatted_request
    assert isinstance(formatted_request["image"], dict)
    assert "source" in formatted_request["image"]
    assert isinstance(formatted_request["image"]["source"], dict)
    assert "imageUri" in formatted_request["image"]["source"]
    assert formatted_request["image"]["source"]["imageUri"] == "url"

    assert "features" in formatted_request
    assert isinstance(formatted_request["features"], list)
    assert isinstance(formatted_request["features"][0], dict)
    assert "type" in formatted_request["features"][0]
    assert formatted_request["features"][0]["type"] == "TEXT_DETECTION"


@patch(
    "summarization.image_caption_detection.requests.post",
    side_effect=mocked_requests_post)
def test_response_for_image_with_caption(mocked_post):
    image_caption_detector = ImageCaptionDetector()
    response_mask = image_caption_detector.get_url_captions_mask(
        ["img_url_with_caption"])
    assert response_mask == [True]


@patch(
    "summarization.image_caption_detection.requests.post",
    side_effect=mocked_requests_post)
def test_response_for_image_without_caption(mocked_post):
    image_caption_detector = ImageCaptionDetector()
    response_mask = image_caption_detector.get_url_captions_mask(
        ["img_url_without_caption"])
    assert response_mask == [False]


@patch(
    "summarization.image_caption_detection.requests.post",
    side_effect=mocked_requests_post)
def test_bad_request(mocked_post):
    image_caption_detector = ImageCaptionDetector()
    with pytest.raises(BadRequestError) as error:
        image_caption_detector.get_url_captions_mask(["bad_url"])
        assert error.message \
            == "The API call was unsuccessful with status code: 400"
