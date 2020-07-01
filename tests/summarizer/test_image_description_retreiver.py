import json
from unittest.mock import Mock, patch

import pytest

from summarization.bad_request_error import BadRequestError
from summarization.web_entity_detection import ImageDescriptionRetriever


def mocked_requests_post(*args, **kwargs):
    json_data = json.loads(kwargs['data'])
    label = ""
    entity = ""
    status_code = 200
    if json_data["requests"][0]["image"]["source"]["imageUri"] \
            == "https://tinyurl.com/y7how2rj":
        label = "sundar pichai"
        entity = "sundar pichai Alphabet"
    elif json_data["requests"][0]["image"]["source"]["imageUri"] \
            == "https://tinyurl.com/y9bvoehm":
        label = "larry page"
        entity = "larry page google"
    elif json_data["requests"][0]["image"]["source"]["imageUri"] \
            == "https://tinyurl.com/y9t35t3z":
        label = "sergey brin"
        entity = "sergey brin google"
    else:
        status_code = 400

    response = json.dumps({
        "responses": [
            {
                "webDetection": {
                    "webEntities": [
                        {
                            "description": entity
                        }
                    ],
                    "bestGuessLabels": [
                        {
                            "label": label,
                            "languageCode": "en"
                        }
                    ]
                }
            }
        ]
    })
    return Mock(status_code=status_code, content=response)


@patch(
    'summarization.web_entity_detection.requests.post',
    side_effect=mocked_requests_post)
def test_request_format(mocked_post):
    image_describer = ImageDescriptionRetriever(1)
    formatted_request = image_describer._format_single_request('url')

    assert isinstance(formatted_request, dict)

    assert "image" in formatted_request
    assert isinstance(formatted_request["image"], dict)
    assert "source" in formatted_request["image"]
    assert isinstance(formatted_request["image"]["source"], dict)
    assert "imageUri" in formatted_request["image"]["source"]
    assert formatted_request["image"]["source"]["imageUri"] == 'url'

    assert "features" in formatted_request
    assert isinstance(formatted_request["features"], list)
    assert isinstance(formatted_request["features"][0], dict)
    assert "maxResults" in formatted_request["features"][0]
    assert "type" in formatted_request["features"][0]
    assert formatted_request["features"][0]["type"] == "WEB_DETECTION"

    assert "imageContext" in formatted_request
    assert isinstance(formatted_request["imageContext"], dict)
    assert "webDetectionParams" in formatted_request["imageContext"]
    assert isinstance(
        formatted_request["imageContext"]["webDetectionParams"], dict)
    assert "includeGeoResults" \
        in formatted_request["imageContext"]["webDetectionParams"]
    assert \
        formatted_request["imageContext"][
            "webDetectionParams"]["includeGeoResults"] \
        == "true"


@ patch(
    'summarization.web_entity_detection.requests.post',
    side_effect=mocked_requests_post)
def test_web_entity_detection(mocked_post):
    image_describer = ImageDescriptionRetriever(1)

    reponse_for_image_url_1 = image_describer.get_description_for_images(
        ["https://tinyurl.com/y7how2rj"])[0]
    assert 'sundar pichai' in reponse_for_image_url_1['label']
    assert 'sundar pichai Alphabet' in reponse_for_image_url_1['entities']

    reponse_for_image_url_2 = image_describer.get_description_for_images(
        ["https://tinyurl.com/y9bvoehm"])[0]
    assert 'larry page' in reponse_for_image_url_2['label']
    assert 'larry page google' in reponse_for_image_url_2['entities']

    reponse_for_image_url_3 = image_describer.get_description_for_images(
        ["https://tinyurl.com/y9t35t3z"])[0]
    assert 'sergey brin' in reponse_for_image_url_3['label']
    assert 'sergey brin google' in reponse_for_image_url_3['entities']


@ patch(
    'summarization.web_entity_detection.requests.post',
    side_effect=mocked_requests_post)
def test_bad_request(mocked_post):
    image_describer = ImageDescriptionRetriever(1)
    with pytest.raises(BadRequestError) as error:
        image_describer.get_description_for_images(["bad_url"])
        assert error.message \
            == "The API call was unsuccessful with status code: 400"


def test_url_batch_splitting_for_multiple_of_batch_size():
    image_describer = ImageDescriptionRetriever(3)
    num_batches = 5
    image_describer.image_urls = [
        "url" for i in range(num_batches * image_describer.BATCH_SIZE)
    ]
    image_describer._split_into_batches()
    batch_split_urls = image_describer.image_url_batches

    assert len(batch_split_urls) == num_batches
    for batch in batch_split_urls:
        assert len(batch) == image_describer.BATCH_SIZE


def test_url_batch_splitting_for_multiple_of_batch_size_minus_one():
    image_describer = ImageDescriptionRetriever(3)
    num_batches = 5
    image_describer.image_urls = [
        "url" for i in range(num_batches * image_describer.BATCH_SIZE - 1)
    ]
    image_describer._split_into_batches()
    batch_split_urls = image_describer.image_url_batches

    assert len(batch_split_urls) == num_batches
    for batch_index in range(num_batches):
        if batch_index == num_batches - 1:
            assert len(batch_split_urls[batch_index]
                       ) == image_describer.BATCH_SIZE - 1
        else:
            assert len(batch_split_urls[batch_index]
                       ) == image_describer.BATCH_SIZE


def test_url_batch_splitting_for_multiple_of_batch_size_plus_one():
    image_describer = ImageDescriptionRetriever(3)
    num_batches = 5
    image_describer.image_urls = [
        "url" for i in range(num_batches * image_describer.BATCH_SIZE + 1)
    ]
    image_describer._split_into_batches()
    batch_split_urls = image_describer.image_url_batches

    assert len(batch_split_urls) == num_batches + 1
    for batch_index in range(num_batches + 1):
        if batch_index == num_batches:
            assert len(batch_split_urls[batch_index]) == 1
        else:
            assert len(batch_split_urls[batch_index]
                       ) == image_describer.BATCH_SIZE


def test_request_ordering():
    image_describer = ImageDescriptionRetriever(3)
    image_describer.all_responses_list = list()
    image_describer.all_responses_list.extend(
        [(1, ["one"]), (0, ["zero"]), (2, ["two"])]
    )
    assert image_describer._get_ordered_and_combined_request_responses() == \
        ["zero", "one", "two"]
