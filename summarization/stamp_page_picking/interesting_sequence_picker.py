''' A module to find the most interesting sequence
of stamp pages that can be displayed to the user
'''
from summarization.stamp_page_picking.max_cover_preprocessor import \
    BudgetedMaxCoverPreprocessor


class InterestingSequencePicker:
    '''
    Finds the most interesting sequence for a
    given list of stamp pages
    Basic outline of algorithm:
    1: initialize seed stamp page
        go to step 2
    2: while stamp_pages can be picked
        > pick stamp page with best interestingness metric
        > remove it from the stamp pages so it wont be
            picked again
        > update last picked stamp page
        go to step 3
    3: if total count of stamp pages
        picked is less then max pages allowed go to step2
        else stop
    '''

    def __init__(
            self,
            stamp_pages,
            summary_sentences,
            max_pages_allowed):
        self.stamp_pages = stamp_pages
        self.summary_sentence_embeddings = [
            sentence.embedding for sentence in
            summary_sentences
        ]
        self.max_pages_allowed = max_pages_allowed

        self.stamp_page_indices = list(range(len(self.stamp_pages)))

        self.cover_size = len(summary_sentences)
        self.picked_cover = [0] * self.cover_size

        # the first stamp page is the title card
        # for the series of stamp pages
        # we will use that as the seed stamp pages
        self.last_picked_stamp_page_index = self.stamp_pages[0]
        self._pick_cover_at_index(0)
        self.stamp_page_indices.pop(0)

        self.threshold = 0.5  # change as required

        # the final sequence that will be returned
        self.stamp_page_sequence = list()

        # unit weight as of now
        # can be changed as per requirement
        self.individual_score_weights = [
            1,  # content change score weight
            1,  # sentiment change score
            1,  # textual entailment score
            1,  # unpicked weights score
            1   # sweeping index score
        ]

        # sweeping index is initially the maximum or last index possible
        self.sweeping_index = max(
            [max(page.media_index, page.sentence_index)
             for page in self.stamp_pages]
        )
        # step size to change sweeping index
        # TODO: add variable change in step size
        # based on iteration
        self.step_size = 1

    def get_interesting_sequence(self):
        for i in range(self.max_pages_allowed):
            # get the index of the next best stamp page
            stamp_page_index = self._get_next_best_stamp_page_index()

            # do not continue if no more stamp pages
            # are left to be picked
            if stamp_page_index == -1:
                break

            # append the stamp page at that index
            self.stamp_page_sequence.append(
                self.stamp_pages[stamp_page_index]
            )

            # update the cover for unpicked weights
            # calculation during next iteration
            self._pick_cover_at_index(stamp_page_index)

            # update the sweeping index
            self._update_sweeping_index()

            # update last picked
            self.last_picked_stamp_page_index = stamp_page_index

        return self.stamp_page_sequence

    def _set_stamp_page_covers(self):
        ''' find covers for stamp pages'''
        preprocessor = BudgetedMaxCoverPreprocessor(
            self.stamp_pages,
            self.summary_sentence_embeddings,
            self.threshold)
        self.stamp_page_covers \
            = preprocessor.get_cover_objects_for_stamp_pages()

    def _pick_cover_at_index(self, index):
        # update the picked_cover
        for i in range(self.cover_size):
            self.picked_cover[i] \
                = self.picked_cover[i] | self.stamp_page_covers[index].cover[i]

    def _get_stamp_page_type(self, stamp_page_index):
        # assign a number to each stamp page type
        stamp_page = self.stamp_pages[stamp_page_index]
        if stamp_page.is_embedded_content:
            return 1
        elif stamp_page.media_index != -1 and stamp_page.sentence_index != -1:
            return 2
        elif stamp_page.media_index != -1:
            return 3
        elif stamp_page.sentence_index != -1:
            return 4

    def _get_content_change_score(self, from_index, to_index):
        # higher change in content type is better
        return abs(
            self._get_stamp_page_type(from_index),
            self._get_stamp_page_type(to_index)
        )

    def _get_unpicked_weights_to_cost_ratio(self, index):
        total_weight = 0
        for i in range(self.cover_size):
            if self.picked_cover[i] == 0 \
                    and self.stamp_page_covers[index].cover[i] == 1:
                total_weight += 1
        return total_weight / self.stamp_page_covers[index].cost

    def _compute_weighted_score(self, score_list):
        return sum(
            [a * b for a, b in zip(score_list, self.individual_score_weights)]
        )

    def _get_approximate_index_for_stamp_page(self, stamp_page_index):
        '''Fetches the approximate index so it can be used
        for computing its distance to the sweepeing index
        '''
        index_sum = 0
        valid_index_count = 0
        stamp_page = self.stamp_pages[stamp_page_index]

        if stamp_page.media_index != -1:
            index_sum += stamp_page.media_index
            valid_index_count += 1

        if stamp_page.sentence_index != -1:
            index_sum += stamp_page.sentence_index
            valid_index_count += 1

        return index_sum / valid_index_count

    def _get_distance_from_sweeping_index(self, stamp_page_index):
        approximate_index = self._get_approximate_index_for_stamp_page(
            stamp_page_index)
        return abs(self.sweeping_index - approximate_index)

    def _interestingess_metric(self, stamp_page_index):
        '''
        calculates the interesting-ness metric based
        on the last picked stamp page
        '''
        from_stamp_page_index = self.last_picked_stamp_page_index
        to_stamp_page_index = stamp_page_index

        content_change_score \
            = self._get_content_change_score(
                from_stamp_page_index,
                to_stamp_page_index
            )

        sentiment_change_score \
            = 0  # will be amended once sentiment detection PR is added

        textual_entailment_score \
            = 0  # will be amended once textual entailment PR is added

        unpicked_weight_cost_ratio_score \
            = self._get_unpicked_weights_to_cost_ratio(stamp_page_index)

        sweeping_index_score = self._get_distance_from_sweeping_index(
            stamp_page_index)

        return self._compute_weighted_score(
            [
                content_change_score,
                sentiment_change_score,
                textual_entailment_score,
                unpicked_weight_cost_ratio_score,
                sweeping_index_score
            ]
        )

    def _update_sweeping_index(self):
        # TODO: amend this to have variable
        # change based on iteration
        self.sweeping_index -= self.step_size

    def _get_next_best_stamp_page_index(self):
        ''' returns the index of the
        next best stamp page to pick given knowledge
        of the last picked stamp page
        '''

        if len(self.stamp_page_indices) == 0:
            return -1

        # sort based on interestingness metric
        self.stamp_page_indices.sort(
            key=self._interestingess_metric, reverse=True)

        # stamp page index at index 0 will have highest score
        next_best_index = self.stamp_page_indices[0]

        # pop the index from indices list so it's not
        # picked again
        self.stamp_page_indices.pop(0)

        return next_best_index
