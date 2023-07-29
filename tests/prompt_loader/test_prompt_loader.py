import threading
import unittest
from moview.modules.prompt_loader.prompt_loader import SingletonPromptLoader
from moview.modules.initial_input.initial_input_analyzer import InitialInputAnalyzer


class TestSingleton(unittest.TestCase):
    def test_singleton(self):
        prompt_loader1 = SingletonPromptLoader()
        prompt_loader2 = SingletonPromptLoader()
        self.assertEqual(id(prompt_loader1), id(prompt_loader2))

    def test_thread_safe(self):
        """
        이 코드는 10개의 스레드를 생성하고, 각 스레드는 Singleton의 인스턴스를 생성하여 instances 리스트에 추가합니다. 모든 스레드가 완료되면, 모든 Singleton 인스턴스가 동일한지 확인하여 스레드에 안전한지 테스트합니다.

        이 테스트를 통과하면, 여러 스레드에서 동시에 Singleton 인스턴스를 생성해도 정확히 하나의 인스턴스만 생성되므로, Singleton이 스레드에 안전함을 확인할 수 있습니다.
        """
        instances = []

        def create_singleton_instance():
            created_instance = SingletonPromptLoader()
            instances.append(created_instance)

        threads = []

        for _ in range(10):  # 10 threads are created
            thread = threading.Thread(target=create_singleton_instance)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()  # Wait until all threads finish

        for instance in instances[1:]:
            self.assertEqual(id(instance), id(instances[0]))


class TestLoadPrompt(unittest.TestCase):
    def test_load_prompt_json(self):
        prompt_loader = SingletonPromptLoader()
        prompt = prompt_loader.load_prompt_json(InitialInputAnalyzer.__name__)

        self.assertTrue(prompt is not None)
        print(prompt)


if __name__ == '__main__':
    unittest.main()
