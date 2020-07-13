'''Image caption detection

This module uses google's cloud vision API's
web entity detection feature for finding the
entities present in an image

The script contains the following classes:
    * ImageCaptiondetector : Detects if the image has some caption present
        and segregates the urls into two lists - one with captions
        and one without
'''

import base64
import concurrent.futures as cf
import json
import os

import requests

from summarization.bad_request_error import BadRequestError


class ImageCaptionDetector:
    '''
    A class to retreive the entities present in an image
    Params:
      maxEntites : maximum number of entity results to return from the api
    '''

    API_ENDPOINT \
        = "https://vision.googleapis.com/v1/images:annotate?key="

    BATCH_SIZE = 5  # number of images per api request

    def __init__(self):
        self.api_key \
            = base64.b64decode(os.environ['GOOGLE_CLOUD_API_KEY'])\
                    .decode("utf-8")
        self.api_url = self.API_ENDPOINT + self.api_key

    def get_url_captions_mask(self, image_urls: list) -> list:
        '''
        Given a list of url detects if the caption is present
        in them
        Params:
        images : list of image paths
        Return type:
        list<bool> : True if the i'th image has a caption or False otherwise
        '''
        self.image_urls = image_urls

        # split into batches based on batch size
        self._split_into_batches()

        # make each request in a single thread
        # this is done since request natively only
        # allows one request per thread
        self._make_concurrent_requests()

        # we need to get the same order as
        # that of the given image_urls
        return self._get_ordered_and_combined_request_responses()

    def _split_into_batches(self):
        self.image_url_batches = list()
        num_image_urls = len(self.image_urls)
        i = 0
        while i < num_image_urls:
            self.image_url_batches.append(
                self.image_urls[i:min(i + self.BATCH_SIZE, num_image_urls)]
            )
            i += self.BATCH_SIZE

    def _make_concurrent_requests(self):
        self.all_responses_list = list()
        executor = cf.ThreadPoolExecutor(max_workers=4)
        future_list = [
            executor.submit(
                self._make_post_request,
                self.image_url_batches[i],
                i) for i in range(len(self.image_url_batches))]
        for future in cf.as_completed(future_list):
            self.all_responses_list.append(future.result())

    def _get_ordered_and_combined_request_responses(self):
        # sort based on request number
        self.all_responses_list.sort()
        caption_detection_results = list()
        for _, img_desc in self.all_responses_list:
            caption_detection_results.extend(img_desc)

        return caption_detection_results

    def _make_post_request(self, image_urls, request_number):
        # request number will be used to order
        # all the requests finally
        image_requests \
            = [self._format_single_request(url) for
               url in image_urls]

        json_data_for_post_request = json.dumps({
            "requests": image_requests
        })
        response = requests.post(self.api_url, data=json_data_for_post_request)

        if response.status_code != 200:
            print(response.content)
            raise BadRequestError(response.status_code)

        response = json.loads(response.content)
        caption_detection_result = list()
        for i in range(len(image_urls)):
            caption_detection_result.append(
                # if the key is present the annotation
                # has been extracted
                "textAnnotations" in response["responses"][i]
            )
        return request_number, caption_detection_result

    def _format_single_request(self, url: str) -> dict:
        '''
        formats the request as a dict
        with the required data and returns it
        Params :
          url: the url of the image
        Return type:
          dict : formatted as shown below
        '''
        return {
            "image": {
                "source": {
                    "imageUri": url
                }
            },
            "features": [
                {
                    "type": "TEXT_DETECTION"
                }
            ]
        }
