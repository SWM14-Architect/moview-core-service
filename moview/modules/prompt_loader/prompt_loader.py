from threading import Lock
import json
import os

# thread-safe singleton 참고 링크
# https://www.kowanas.com/coding/2020/11/29/%EC%8B%B1%EA%B8%80%ED%86%A4-%ED%8C%A8%ED%84%B4/

# 싱글톤 패턴이 적용된 metaclass.
# metaclass는 클래스를 만드는 클래스이다.
"""
메타클래스는 여기서 클래스의 생성과 관리 책임을 담당하며, 실제 비즈니스 로직은 Singleton 클래스가 담당합니다. 메타클래스는 기본적으로 클래스의 동작을 변경하는 역할을 합니다.

메타클래스 SingletonMeta의 __call__ 메소드에서는 Singleton 클래스의 인스턴스를 생성하거나 기존 인스턴스를 반환하는 로직을 관리합니다. 한편, 실제 비즈니스 로직은 Singleton 클래스 안에 구현됩니다.

이렇게 분리함으로써, 클래스 생성 및 관리와 실제 비즈니스 로직이 명확히 분리되고, 각각의 책임이 명확해집니다. 이는 소프트웨어 디자인 원칙인 단일 책임 원칙(Single Responsibility Principle)을 따르는 것이며, 이를 통해 코드의 가독성과 유지 보수성을 향상시킬 수 있습니다.
"""


class SingletonPromptLoaderMeta(type):
    _instance = None
    _lock = Lock()

    # 객체가 생성을 호출하면, __call__ 메소드가 호출된다.
    def __call__(cls, *args, **kwargs):
        # lock을 걸어서 thread-safe하게 만든다.
        # 이렇게 하면 여러 스레드가 동시에 호출할 때 인스턴스가 여러번 생성되는 걸 방지할 수 있음.
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class SingletonPromptLoader(metaclass=SingletonPromptLoaderMeta):
    def load_prompt_json(self, class_name: str) -> dict:
        """
        json 파일을 읽어서 prompt를 반환하는 메서드
        Args:
            class_name: prompt를 사용할 class 이름. __name__을 사용하면 됨.

        Returns: 프롬프트 내용

        """

        if class_name == 'InterviewAnswerScorer':
            raise ValueError('InterviewAnswerScorer는 이 메서드를 사용할 수 없습니다.')

        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/json/' + class_name + '.json', 'r') as f:
            data = json.load(f)

        return data['prompt']

    def load_multi_prompt_chain_json_for_interview_answer_scorer(self, class_name: str) -> dict:
        if class_name != 'InterviewAnswerScorer':
            raise ValueError('InterviewAnswerScorer만 이 메서드를 사용할 수 있습니다.')

        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/json/' + class_name + '.json', 'r') as f:
            data = json.load(f)

        return data['multi_prompt_template']

    def load_routing_prompt_json_for_interview_answer_scorer(self, class_name: str) -> dict:
        if class_name != 'InterviewAnswerScorer':
            raise ValueError('InterviewAnswerScorer만 이 메서드를 사용할 수 있습니다.')

        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/json/' + class_name + '.json', 'r') as f:
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

        return self.__combine_templates(data, keys)

    def __combine_templates(self, data: dict, keys: dict):
        return {
            key: data['header_template'] + data[template] + data.get('footer_template', '')
            for key, template in keys.items()
        }
