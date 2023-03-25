import random
from typing import List


class LangHeader:
    def __init__(self, main_lang: str, langs: List[str] = []):
        self.main_lang = main_lang
        self.langs = langs

    def generate(self):
        header = []
        total_weight = 0

        lang_prob = {self.main_lang: 2}
        total_weight += 2

        for lang in self.langs:
            lang_prob[lang] = 1
            total_weight += 1

        selected_langs = random.choices(list(lang_prob.keys()), weights=list(lang_prob.values()), k=len(self.langs))

        header.append(f"{self.main_lang};q=1.0")

        q_val = 0.9
        for lang in selected_langs:
            if lang != self.main_lang:
                header.append(f"{lang};q={q_val:.1f}")
                q_val -= 0.1

        header_str = ','.join(header)

        return {'Accept-Language': header_str}
