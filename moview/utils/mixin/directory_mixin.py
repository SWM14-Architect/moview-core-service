class DirectoryMixin:
    """
    Python에서 믹스인(Mixin)은 특정 클래스에 메서드를 제공하기 위해 다른 클래스에 "믹스인"될 수 있는 클래스를 말합니다. 믹스인은 다른 클래스의 기능을 확장하거나 수정할 목적으로 사용되며, 보통 단독으로는 인스턴스화되지 않습니다. 이는 다중 상속의 한 형태로서, 여러 클래스에서 필요로 하는 공통 기능을 제공하는 재사용 가능한 클래스입니다.

    믹스인의 주요 목적은 코드 중복을 줄이고, 클래스 간에 기능을 공유하여 각 클래스를 더 작고, 관리하기 쉽고, 단일 책임 원칙을 따르도록 만드는 것입니다.
    """

    @classmethod
    def get_module_name(cls):
        """

        Returns: 클래스를 포함하는 모듈 이름을 반환합니다.

        (예시) moview.service.answer.followup_question_determiner

       """
        return cls.__module__

    @classmethod
    def get_class_name(cls):
        """

        Returns: 클래스 이름을 반환합니다.
        (예시) FollowupQuestionDeterminer

        """
        return cls.__name__

    @classmethod
    def get_full_class_name(cls):
        """

        Returns: 클래스의 모듈 이름과 클래스 이름을 반환합니다.
        (예시) moview.service.answer.followup_question_determiner.FollowupQuestionDeterminer

        """
        return cls.get_module_name() + "." + cls.get_class_name()
