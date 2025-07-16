import json
import random
from typing import List, Optional, Dict, Any

class TextLib:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.questions = self._load_questions()

    def _load_questions(self) -> List[Dict[str, Any]]:
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_random_question(self, qtype: Optional[str] = None, language: Optional[str] = None, difficulty: Optional[str] = None) -> Optional[Dict[str, Any]]:
        filtered = self.questions
        if qtype:
            filtered = [q for q in filtered if q.get('type') == qtype]
        if language:
            filtered = [q for q in filtered if q.get('language') == language]
        if difficulty:
            filtered = [q for q in filtered if q.get('difficulty') == difficulty]
        if not filtered:
            return None
        return random.choice(filtered)

    def get_all_types(self) -> List[str]:
        return list(set(q.get('type', '') for q in self.questions))

    def get_all_languages(self) -> List[str]:
        return list(set(q.get('language', '') for q in self.questions))

# 用法示例：
# lib = TextLib('textlib/questions.json')
# q = lib.get_random_question(qtype='code', language='zh')
# print(q) 