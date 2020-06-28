''' A module to find the most interesting sequence
of stamp pages that can be displayed to the user
'''
from summarization.stamp_page_picking.max_cover_preprocessor import \
    BudgetedMaxCoverPreprocessor


class InterestingSequencePicker:

    def __init__(
            self,
            seed_stamp_page,
            stamp_pages,
            summary_sentences,
            max_pages_allowed):
        self.seed_stamp_page = seed_stamp_page
        self.stamp_pages = stamp_pages
        self.summary_sentence_embeddings = [
            sentence.embedding for sentence in self.summary_sentence_embeddings
        ]
        self.max_pages_allowed = max_pages_allowed
        self.threshold = 0.5
        self.stamp_pages_count = len(self.stamp_pages)
        self.max_index = float('inf')

    def _set_cover_objects_for_stamp_pages(self):
        preprocessor = BudgetedMaxCoverPreprocessor(
            self.stamp_pages, self.summary_sentence_embeddings, self.threshold)
        self.stamp_page_covers = preprocessor.get_cover_objects_for_stamp_pages()
        self.number_of_elements = len(self.stamp_page_covers[0].cover)

    def _initialize_variables_for_sequence_picking(self):
        self.candidate_stamp_page_covers = self.stamp_page_covers
        self.is_element_picked = [0] * self.number_of_elements
        self.last_picked_stamp_page_cover = self.seed_stamp_page
        self.picked_stamp_pages = list()
        self.sweeping_index = self.max_index

    def get_interesting_sequence(self):
        self._initialize_variables_for_sequence_picking()
        for i in range(self.max_pages_allowed):
            stamp_page_index = self._get_next_best_stamp_page_index()
            self.picked_stamp_pages.append(self.stamp_pages[stamp_page_index])

    def _get_weight_to_cost_ratio(self, stamp_page_cover):
        weight_sum = 0
        for i in range(self.number_of_elements):
            if stamp_page.cover[i] != 0 and self.is_element_picked[i] == 0:
                weight_sum += stamp_page.cover[i]
        return weight_sum / stamp_page.cost

    def _get_distance_from_sweeping_index(self, stamp_page_cover):
        total_index = 0
        total_valid_indices = 0
        if self.stamp_pages[stamp_page_cover.id].sentence_index != -1:
            total_index += self.stamp_pages[stamp_page_cover.id].sentence_index
            total_valid_indices += 1

        if self.stamp_pages[stamp_page_cover.id].media_index != -1:
            total_index += self.stamp_pages[stamp_page_cover.id].media_index
            total_valid_indices += 1

        overall_index = total_index / total_valid_indices

        return abs(self.sweeping_index - overall_index)

    def _get_textual_entailment_cost(self, stamp_page_cover):
        # TODO: amend this block
        return 1

    def _get_change_in_stamp_page_types_cost(
            self, from_stamp_page_cover, to_stamp_page_cover):
        # TODO: amend this block
        return 1

    def _interestingness_factor_for_transition(self, stamp_page_cover):
        from_stamp_page_cover = self.last_picked_stamp_page_cover
        to_stamp_page_cover = stamp_page_cover

        # define attributes to be used in the formula for scoring
        weight_to_cost_ratio = self._get_weight_to_cost_ratio(
            to_stamp_page_cover)
        sweeping_distance_cost = self._get_distance_from_sweeping_index(
            to_stamp_page_cover)
        textual_entailment_cost = self._get_textual_entailment_cost(
            to_stamp_page_cover)

        # combine this in a different way?
        return weight_to_cost_ratio + sweeping_distance_cost + textual_entailment_cost

    def _get_next_best_stamp_page_index(self):
        self.candidate_stamp_page_covers.sort(
            key=self._interestingness_factor_for_transition)
        return 0
