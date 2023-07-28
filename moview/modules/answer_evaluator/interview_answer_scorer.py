import json
import os

from langchain.chains.router import MultiPromptChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

CATEGORIES = ["Behavioral Questions", "Situational Questions", "Technical Job-related Questions",
              "Cultural Fit Questions", "Personal Character Questions"]

SUB_CATEGORIES = {
    "Behavioral Questions": ["Details", "Results and Learnings", "Reaction and Coping Strategies"],
    "Situational Questions": ["Job-related Scenarios", "Scenarios Reflecting Company Culture and Values",
                              "Adaptability and Problem-solving Skills", "Ethical Judgment"],
    "Technical Job-related Questions": ["Technical Details", "Real-world Application",
                                        "Learning and Development"],
    "Cultural Fit Questions": ["Core Values and Principles of the Company", "Teamwork and Communication Style",
                               "Candidate's Traits and Values", "Adaptability"],
    "Personal Character Questions": ["Thinking Style and Behavioral Patterns", "Growth and Development",
                                     "Motivation and Values"]
}


class InterviewAnswerScorer:
    def __init__(self):
        self.prompt = self.__load_prompt_for_multi_prompt_chain_from_json_file()
        self.templates_for_prompt_info = self.__load_prompt_for_routing_from_json_file()

    def score_by_main_and_subcategories(self, question: str, answer: str, categories_ordered_pair: str) -> str:

        multi_prompt_chain = self.__make_multi_prompt_chain()

        return multi_prompt_chain.run(
            self.prompt.format(categories_ordered_pair=categories_ordered_pair, question=question, answer=answer)
        )

    def __load_prompt_for_multi_prompt_chain_from_json_file(self):
        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/score_category.json', 'r') as f:
            data = json.load(f)

        return data['multi_prompt_template']

    def __load_prompt_for_routing_from_json_file(self):
        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/score_category.json', 'r') as f:
            data = json.load(f)

        return {
            "Details": data['details_template'],
            "Results and Learnings": data['results_learnings_template'],
            "Reaction and Coping Strategies": data['coping_strategies_template'],
            "Job-related Scenarios": data['job_scenarios_template'],
            "Scenarios Reflecting Company Culture and Values": data['culture_values_template'],
            "Adaptability and Problem-solving Skills": data['problem_solving_template'],
            "Ethical Judgment": data['ethical_judgment_template'],
            "Technical Details": data['tech_details_template'],
            "Real-world Application": data['real_world_application_template'],
            "Learning and Development": data['learning_development_template'],
            "Core Values and Principles of the Company": data['core_values_principles_template'],
            "Teamwork and Communication Style": data['teamwork_communication_template'],
            "Candidate's Traits and Values": data['candidate_traits_values_template'],
            "Adaptability": data['adaptability_template'],
            "Thinking Style and Behavioral Patterns": data['thinking_style_behavioral_patterns_template'],
            "Growth and Development": data['growth_development_template'],
            "Motivation and Values": data['motivation_values_template']
        }

    def __make_multi_prompt_chain(self):
        llm_router = ChatOpenAI(model_name='gpt-3.5-turbo',
                                streaming=True, callbacks=[StreamingStdOutCallbackHandler()])

        prompt_info = self.__create_prompt_info()

        destinations = [f"{p['name']}: {p['description']}" for p in
                        prompt_info]

        destinations_str = "\n".join(destinations)

        router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
            destinations=destinations_str)

        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
            output_parser=RouterOutputParser(),
        )
        router_chain = LLMRouterChain.from_llm(llm_router, router_prompt)

        destination_chains = {}

        for p_info in prompt_info:
            name = p_info["name"]
            prompt_template = p_info["prompt_template"]
            prompt = PromptTemplate(template=prompt_template,
                                    input_variables=["input"])
            destination_chains[name] = LLMChain(llm=llm_router, prompt=prompt)

        multi_prompt_chain = MultiPromptChain(
            router_chain=router_chain,
            destination_chains=destination_chains,
            default_chain=ConversationChain(llm=ChatOpenAI(), output_key="text"))

        return multi_prompt_chain

    def __create_prompt_info(self):
        prompt_info = []

        for category in CATEGORIES:
            for sub_category in SUB_CATEGORIES[category]:
                prompt_name = f"{category}, {sub_category}"
                prompt_description = f"This question and response pertain to the '{category}' area and '{sub_category}' sub area."
                prompt_template = self.templates_for_prompt_info[sub_category]

                prompt_info.append(
                    {
                        "name": prompt_name,
                        "description": prompt_description,
                        "prompt_template": prompt_template,
                    })

        return prompt_info
