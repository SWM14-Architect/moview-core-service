import json
import os

from moview.utils.singleton_meta_class import SingletonMeta


class PromptLoader(metaclass=SingletonMeta):

    @staticmethod
    def load_prompt_json(class_name: str) -> dict:
        """
        json 파일을 읽어서 prompt를 반환하는 메서드
        Args:
            class_name: prompt를 사용할 class 이름. __name__을 사용하면 됨.

        Returns: 프롬프트 내용

        """

        if class_name == 'InterviewAnswerScorer':
            raise ValueError('InterviewAnswerScorer는 이 메서드를 사용할 수 없습니다.')

        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/json/' + class_name + '.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data['prompt']

    @staticmethod
    def load_multi_prompt_chain_json_for_interview_answer_scorer(class_name: str) -> dict:
        if class_name != 'AnswerScorer':
            raise ValueError('AnswerScorer만 이 메서드를 사용할 수 있습니다.')

        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/json/' + class_name + '.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data['multi_prompt_template']

    @staticmethod
    def load_routing_prompt_json_for_interview_answer_scorer(class_name: str) -> dict:
        if class_name != 'AnswerScorer':
            raise ValueError('AnswerScorer만 이 메서드를 사용할 수 있습니다.')

        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/json/' + class_name + '.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        keys = {
            "Details": 'details_template',
            "Results and Learnings": 'results_learnings_template',
            "Reaction and Coping Strategies": 'coping_strategies_template',
            "Job-related Scenarios": 'job_scenarios_template',
            "Scenarios Reflecting Company Culture and Values": 'culture_values_template',
            "Adaptability and Problem-solving Skills": 'problem_solving_template',
            "Ethical Judgment": 'ethical_judgment_template',
            "Technical Details": 'tech_details_template',
            "Real-world Application": 'real_world_application_template',
            "Learning and Development": 'learning_development_template',
            "Core Values and Principles of the Company": 'core_values_principles_template',
            "Teamwork and Communication Style": 'teamwork_communication_template',
            "Candidate's Traits and Values": 'candidate_traits_values_template',
            "Adaptability": 'adaptability_template',
            "Thinking Style and Behavioral Patterns": 'thinking_style_behavioral_patterns_template',
            "Growth and Development": 'growth_development_template',
            "Motivation and Values": 'motivation_values_template'
        }

        return PromptLoader.__combine_templates(data, keys)

    @staticmethod
    def __combine_templates(data: dict, keys: dict):
        return {
            key: data['header_template'] + data[template] + data.get('footer_template', '')
            for key, template in keys.items()
        }
