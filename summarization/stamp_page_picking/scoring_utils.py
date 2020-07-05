''' Module for scoring utils '''

from sklearn.metrics.pairwise import cosine_similarity


class ScoringUtils:
    def __init__(self, stamp_pages, stamp_page_covers, cover_size):
        self.stamp_pages = stamp_pages
        self.stamp_page_covers = stamp_page_covers
        self.cover_size = cover_size
        self.picked_cover = [0] * self.cover_size

        # sweeping index is initially the maximum or last index possible
        self.sweeping_index = max(
            [max(page.media_index, page.sentence_index)
             for page in self.stamp_pages]
        )

        self.last_picked_stamp_page_index = -1

        # step size to change sweeping index
        # TODO: add variable change in step size
        # based on iteration
        self.step_size = 1
        self.iteration_count = 1

        self.individual_score_weights = [
            1,  # content change score weight
            1,  # sentiment change score
            1,  # textual entailment score
            1,  # unpicked weights/cost score - as used in max cover
                # it tells how many sentences in the web-page are
                # unpicked yet and its ratio to stamp page cost
            1   # sweeping index score
        ]

    def _update_last_picked_stamp_page(self, stamp_index):
        self.last_picked_stamp_page_index = stamp_index

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

        content_similarity_score = self._get_content_similarity_score(
            from_stamp_page_index, to_stamp_page_index)

        unpicked_weight_cost_ratio_score \
            = self._get_unpicked_weights_to_cost_ratio_score(stamp_page_index)

        sweeping_index_score = self._get_distance_from_sweeping_index(
            stamp_page_index)

        return self._compute_weighted_score(
            [
                content_change_score,
                sentiment_change_score,
                content_similarity_score,
                unpicked_weight_cost_ratio_score,
                sweeping_index_score
            ]
        )

    def _pick_stamp_page_cover_at_index(self, index):
        # update the picked_cover
        for i in range(self.cover_size):
            self.picked_cover[i] \
                = self.picked_cover[i] | self.stamp_page_covers[index].cover[i]

    def _get_content_change_score(self, from_index, to_index):
        # higher change in content type is better
        return abs(
            self._get_stamp_page_type(from_index)
            - self._get_stamp_page_type(to_index)
        )

    def _get_unpicked_weights_to_cost_ratio_score(self, index):
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

    def _get_content_similarity_score(self, from_index, to_index):
        ''' Gets the similarity with the previously picked stamp page'''
        return cosine_similarity(
            [self.stamp_pages[from_index].stamp_descriptor_embedding],
            [self.stamp_pages[to_index].stamp_descriptor_embedding]
        )[0]

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

    def _update_sweeping_index(self):
        self.iteration_count += 1
        self.sweeping_index -= self.step_size * self.iteration_count
