from moview.environment.environment_loader import EnvironmentLoader

OPENAI_API_KEY_PARAM = "openai-api-key"


# 아래 코드는 팩토리 메서드 패턴이나 추상 팩토리 패턴이 적용된 것이 아닙니다.
# Simple Factory 패턴인데, 엄밀히 말하면 디자인 패턴은 아닙니다.
class LLMModelFactory:
    """
    정적 메서드는 self를 받지 않으므로 인스턴스 속성에는 접근할 수 없습니다. 그래서 보통 정적 메서드는 인스턴스 속성, 인스턴스 메서드가 필요 없을 때 사용합니다.
    정적 메서드는 순수 함수(pure function)를 만들 때 사용합니다. 순수 함수는 부수 효과(side effect)가 없고 입력 값이 같으면 언제나 같은 출력 값을 반환합니다. 즉, 정적 메서드는 인스턴스의 상태를 변화시키지 않는 메서드를 만들 때 사용합니다.

    model_name list				TPM		RPM
    gpt-3.5-turbo				90,000	3,500
    gpt-3.5-turbo-0301			90,000	3,500
    gpt-3.5-turbo-0613			90,000	3,500
    gpt-3.5-turbo-16k			180,000	3,500
    gpt-3.5-turbo-16k-0613		180,000	3,500
    gpt-3.5-turbo-instruct		250,000	3,000
    gpt-3.5-turbo-instruct-0914	250,000	3,000
    gpt-4						10,000	200
    gpt-4-0314					10,000	200
    gpt-4-0613					10,000	200
    """

    @staticmethod
    def load_api_key_for_open_ai() -> str:
        return EnvironmentLoader.getenv(OPENAI_API_KEY_PARAM)
