"""2.1 request contract tests; all HTTP is mocked, no real keys or paid calls."""
import base64
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('nano21_provider', ROOT / 'nanobanana_pro_node.py')
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)
MODEL = 'gemini-nano-banana-2.1'


def picture(color):
    stream = io.BytesIO()
    Image.new('RGB', (8, 8), color).save(stream, format='PNG')
    return {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(stream.getvalue()).decode()}}


class Nano21Tests(unittest.TestCase):
    def setUp(self):
        self.node = provider.NanoBananaProImageGenerator()
        self.response = Mock(status_code=200)
        self.response.json.return_value = {'candidates': [{'content': {'parts': [
            {'text': 'draft'}, picture('red'), {'text': 'final'}, picture('blue'), {'text': 'done'}]}}]}
        blocker = patch.object(provider.requests.sessions.Session, 'request', side_effect=AssertionError('Live HTTP forbidden'))
        blocker.start()
        self.addCleanup(blocker.stop)
        post = patch.object(provider.requests, 'post', return_value=self.response)
        self.post = post.start()
        self.addCleanup(post.stop)

    def generate(self, model=MODEL, thinking='disabled', ratio='16:9', size='2K', image=None):
        return self.node._generate_one('fake-test-key', model, thinking, 'test', ratio, size, 0, image)

    def test_dropdown_preserves_inputs_and_models(self):
        schema = self.node.INPUT_TYPES()['required']
        self.assertEqual(schema['model_version'][0], ['gemini-3-pro-image-preview', 'gemini-3.1-flash-image-preview', MODEL])
        self.assertEqual(len(schema['aspect_ratio'][0]), 15)  # auto + 14 ratios
        self.assertEqual(schema['model_version'][1]['default'], 'gemini-3-pro-image-preview')

    def test_request_mapping_and_final_image(self):
        for size in ('1K', '2K', '4K'):
            for level, expected in [('disabled', None), ('low', 'minimal'), ('minimal', 'minimal'), ('medium', 'medium'), ('high', 'high')]:
                with self.subTest(size=size, level=level):
                    tensor, _, error = self.generate(thinking=level, size=size, ratio='8:1')
                    self.assertIsNone(error)
                    self.assertEqual(tensor[0, 0, 0].tolist(), [0., 0., 1.])
                    args, kwargs = self.post.call_args
                    self.assertTrue(args[0].endswith('/v1beta/models/' + MODEL + ':generateContent'))
                    self.assertEqual(kwargs['timeout'], 360)
                    self.assertEqual(kwargs['headers']['Authorization'], 'Bearer fake-test-key')
                    cfg = kwargs['json']['generationConfig']
                    self.assertEqual(cfg['imageConfig'], {'imageSize': size, 'aspectRatio': '8:1'})
                    self.assertEqual(cfg.get('thinkingConfig', {}).get('thinkingLevel'), expected)

    def test_edit_and_auto_ratio(self):
        _, _, error = self.generate(ratio='auto', image=torch.zeros((2, 8, 64, 3)))
        self.assertIsNone(error)
        body = self.post.call_args.kwargs['json']
        parts = body['contents'][0]['parts']
        self.assertEqual([set(p) for p in parts], [{'text'}, {'inlineData'}, {'inlineData'}])
        self.assertEqual(body['generationConfig']['imageConfig']['aspectRatio'], '8:1')

    def test_invalid_settings_never_send_http(self):
        for settings in [dict(size='512'), dict(thinking='invalid'), dict(model='gemini-3-pro-image-preview', ratio='8:1')]:
            self.assertIsNotNone(self.generate(**settings)[2])
        self.post.assert_not_called()

    def test_legacy_request_and_first_image_unchanged(self):
        for model in ('gemini-3-pro-image-preview', 'gemini-3.1-flash-image-preview'):
            tensor, _, error = self.generate(model=model, thinking='low')
            self.assertIsNone(error)
            self.assertEqual(tensor[0, 0, 0].tolist(), [1., 0., 0.])
            self.assertEqual(self.post.call_args.kwargs['timeout'], 300)
            cfg = self.post.call_args.kwargs['json']['generationConfig']
            self.assertEqual(cfg.get('thinkingConfig', {}).get('thinkingLevel'), 'low' if '3.1' in model else None)

    def test_empty_parts_is_failure(self):
        self.response.json.return_value = {'candidates': [{'content': {'parts': None}, 'finishReason': 'IMAGE_SAFETY'}]}
        self.assertIsNotNone(self.generate()[2])

    def test_immediate_adapter_uses_selected_model(self):
        spec = importlib.util.spec_from_file_location('nano21_backend', ROOT / 'api_immediate/backend.py')
        backend = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(backend)
        inputs = {name: options[1].get('default', options[0][0] if isinstance(options[0], list) else '')
                  for name, options in self.node.INPUT_TYPES()['required'].items()}
        inputs.update(api_key='fake-test-key', model_version=MODEL, thinking_level='high', image_count=2)
        payload = {'target': '1', 'prompt': {'1': {'class_type': 'NanoBananaPro', 'inputs': inputs}}}
        backend.validate(payload, provider.NODE_CLASS_MAPPINGS)
        count, request, _ = backend.prepare(payload, provider.NODE_CLASS_MAPPINGS)
        self.assertEqual(count, 2)
        self.assertIsNone(request(0)[1])
        self.assertIn(MODEL, self.post.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
