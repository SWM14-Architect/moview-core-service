from langchain.chains.router import MultiPromptChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from moview.modules.prompt_loader.prompt_loader import PromptLoader

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
        prompt_loader = PromptLoader()

        self.multi_prompt = prompt_loader.load_multi_prompt_chain_json_for_interview_answer_scorer(
            InterviewAnswerScorer.__name__)
        self.prompt_info_for_router_chain = prompt_loader.load_routing_prompt_json_for_interview_answer_scorer(
            InterviewAnswerScorer.__name__)

    def rate_by_main_and_subcategories(self, question: str, answer: str, categories_ordered_pair: str) -> str:

        multi_prompt_chain = self.__make_multi_prompt_chain()

        return multi_prompt_chain.run(
            self.multi_prompt.format(categories_ordered_pair=categories_ordered_pair, question=question, answer=answer)
        )

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
                prompt_template = self.prompt_info_for_router_chain[sub_category]

                prompt_info.append(
                    {
                        "name": prompt_name,
                        "description": prompt_description,
                        "prompt_template": prompt_template,
                    })

        return prompt_info
