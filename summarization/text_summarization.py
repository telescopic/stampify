''' Module to perform text summarization'''

from gensim.summarization.summarizer import summarize
from nltk.tokenize import sent_tokenize
from summarizer import Summarizer
from summarizer.coreference_handler import CoreferenceHandler

from summarization.incorrect_input import IncorrectInputError
from summarization.text_entity_detection import TextEntityRetriever


class TextSummarizer:
    """
    A class to perform summarization on english text

    Attributes:
        text_summarizer : will hold the summarizer chosen
        on the basis of priority

    Methods:
        - summarize_text (text , ratio):
            Given the text and ratio
            returns the summarized text
    """

    def __init__(self, priority):
        '''
        Initializes the text rank or bert summarizers
        based on priority

        priority should be either accuracy or speed
        based on which we can choose either a
        low speed high accuracy summarizer - bert
        high speed lower accuracy summarizer - textRank
        '''
        self.text_summarizer = None
        if priority == "accuracy":
            handler = CoreferenceHandler(greedyness=.4)
            self.text_summarizer = Summarizer(
                model='distilbert-base-uncased',
                sentence_handler=handler)
        elif priority == "speed":
            self.text_summarizer = summarize
        else:
            raise IncorrectInputError(
                "priority must be either accuracy or speed")

    def _get_entites_from_text(self):
        entity_retriever = TextEntityRetriever()
        self.entity_list = entity_retriever.get_entities_from_text(self.text)

    def summarize_text(self, text: str, ratio=0.4):
        '''
            Finds the summarization for a given text

            Parameters:
                - text : the text to be summarized
                - ratio : value in range [0,1] - what % of the text to retain
        '''
        if ratio < 0 or ratio > 1:
            raise IncorrectInputError(
                "Ratio should be in the range of [0,1] ")

        self.text = text

        # get the entities in the text and store it
        # in a list
        self._get_entites_from_text()
        sentence_tokenized_text = sent_tokenize(text)

        text_with_entities_list = list()

        # separate sentences into two:
        # those that contain entities
        # and those that don't
        for sentence in sentence_tokenized_text:
            sentence_has_entity = False

            for entity in self.entity_list:
                if entity in sentence:
                    sentence_has_entity = True

            if sentence_has_entity:
                text_with_entities_list.append(sentence)

        # summarize the sentence that don't have entities
        tokenized_summarized_text \
            = sent_tokenize(
                self.text_summarizer(text, ratio)
            )

        # combines both enetity and non-entity sentences
        # in ORDER
        # order is necessary so the indexing
        # is preserved
        combined_summarized_text_list = list()

        # iterate over the un-summarized sentences
        # if the sentence has an entity or is in
        # the summarized sentences list add it to
        # the combined summarized list

        for sentence in sentence_tokenized_text:
            sentence_has_entity = False

            for entity in self.entity_list:
                if entity in sentence:
                    sentence_has_entity = True

            if sentence_has_entity or sentence in tokenized_summarized_text:
                combined_summarized_text_list.append(sentence)

        return ' '.join(combined_summarized_text_list)
