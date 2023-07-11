import unittest
from moview.utils.data_manager import *
from unittest.mock import Mock
from moview.modules.analyzer.answer_analyzer import AnswerAnalyzer
from langchain.prompts import PromptTemplate


# LLM Call은 테스트하지 않습니다.
# 프롬프트 제작이 되는 지만 테스트합니다.

class TestAnswerAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_data_manager = Mock(spec=DataManager)

        self.mock_question_entity = Mock(spec=QuestionEntity)
        self.mock_question_entity.question = "테스트 질문"
        self.mock_question_entity.answer = "테스트 답변"

        self.evaluation_manager = Mock(spec=EvaluationManager)
        self.answer_analyzer = AnswerAnalyzer(
            self.mock_data_manager,
            self.mock_question_entity,
            self.evaluation_manager,
        )

    def test__make_specific_prompt_with_knowledge_whether_it_has_all_fit(self):
        # given
        fit_feature_dict = self.answer_analyzer.fit_feature_dict

        # when
        prompt_info_array = self.answer_analyzer._make_specific_prompt_with_knowledge()

        # then
        for prompt_info in prompt_info_array:
            fit_name = prompt_info["name"]
            # dict에 없으면 실패하게 했습니다. 즉, 모두 dict에 있으면 테스트 통과입니다.
            if fit_name not in fit_feature_dict:
                self.fail("fit_name is not in fit_feature_dict")
            else:
                print(fit_name + " is in fit_feature_dict")

    def test__make_specific_prompt_with_knowledge_whether_it_has_all_description(self):
        # given
        knowledge_prompt = self.answer_analyzer._make_knowledge_prompt()
        fit_feature_dict = self.answer_analyzer.fit_feature_dict

        # when
        prompt_info_array = self.answer_analyzer._make_specific_prompt_with_knowledge()

        # then
        for prompt_info in prompt_info_array:
            fit_feature = prompt_info["name"]

            review_standard_knowledge = fit_feature_dict[fit_feature][0]
            review_standard_detail = fit_feature_dict[fit_feature][1]

            description_prompt = PromptTemplate.from_template(knowledge_prompt) \
                .format(review_standard_knowledge=review_standard_knowledge,
                        review_standard_detail=review_standard_detail)

            print(description_prompt)

            self.assertEqual(prompt_info["description"], description_prompt)
