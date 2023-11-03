import random
from moview.utils.mixin.directory_mixin import DirectoryMixin


class FollowupQuestionDeterminer(DirectoryMixin):

    @staticmethod
    def need_to_give_followup_question() -> bool:
        base_probability_of_question = 0.5

        need = random.random() < base_probability_of_question

        return need
