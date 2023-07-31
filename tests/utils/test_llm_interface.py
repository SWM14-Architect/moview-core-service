import unittest
from moview.envrionment.llm_factory import LLMApiKeyLoader


class TestLLMApiKeyLoader(unittest.TestCase):
    def test_singleton(self):
        key_loader1 = LLMApiKeyLoader()
        key_loader2 = LLMApiKeyLoader()
        self.assertEqual(id(key_loader1), id(key_loader2))

    def test_singleton_init_called(self):
        key_loader1 = LLMApiKeyLoader()
        key_loader2 = LLMApiKeyLoader()
        self.assertTrue(key_loader1.openai_api_key is not None)
        self.assertTrue(key_loader2.openai_api_key is not None)
        self.assertTrue(key_loader1.openai_api_key == key_loader2.openai_api_key)
