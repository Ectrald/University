import random
from typing import List, Tuple


class MorphoEntry:
    """
    Класс, представляющий одну лексему в словаре.
    Хранит основу (лемму), часть речи и сгенерированные словоформы.
    """
    def __init__(self, lemma: str, pos: str):
        self.lemma = lemma
        self.pos = pos
        self.forms = self._generate_forms()

    def _generate_forms(self) -> dict:
        """
        Генерация основных форм на основе простых правил английского языка.
       
        """
        forms = {'base': self.lemma}
        
        if self.pos == 'NOUN':
            if self.lemma.endswith(('s', 'x', 'z', 'ch', 'sh')):
                forms['plural'] = self.lemma + 'es'
            elif self.lemma.endswith('y') and len(self.lemma) > 1 and self.lemma[-2] not in 'aeiou':
                forms['plural'] = self.lemma[:-1] + 'ies'
            else:
                forms['plural'] = self.lemma + 's'
                
        elif self.pos == 'VERB':
            if self.lemma.endswith('e'):
                forms['past'] = self.lemma + 'd'
                forms['gerund'] = self.lemma[:-1] + 'ing'
            else:
                forms['past'] = self.lemma + 'ed'
                forms['gerund'] = self.lemma + 'ing'
            forms['3rd_person'] = self.lemma + 's'

        elif self.pos == 'ADJ':
            if len(self.lemma) <= 5: 
                forms['comp'] = self.lemma + 'er'
                forms['super'] = self.lemma + 'est'
            else:
                forms['comp'] = 'more ' + self.lemma
                forms['super'] = 'most ' + self.lemma
                
        return forms

    def get_form(self, form_tag: str) -> str:
        return self.forms.get(form_tag, self.lemma)


class MorphoDictionary:

    def __init__(self):
        self.entries = {}  
        self.by_pos = {'NOUN': [], 'VERB': [], 'ADJ': [], 'ADV': []}

    def load_words(self, word_list: List[Tuple[str, str]]):

        for lemma, pos in word_list:
            if pos not in self.by_pos:
                continue
            
            if lemma not in self.entries:
                entry = MorphoEntry(lemma, pos)
                self.entries[lemma] = entry
                self.by_pos[pos].append(entry)
                
    def get_random(self, pos: str = None) -> MorphoEntry:
        if pos:
            candidates = self.by_pos.get(pos, [])
            return random.choice(candidates) if candidates else None
        else:
            all_words = list(self.entries.values())
            return random.choice(all_words) if all_words else None


class RandomSynthesizer:

    def __init__(self, dictionary: MorphoDictionary):
        self.dictionary = dictionary

    def synthesize(self) -> str:

        max_attempts = 20
        for _ in range(max_attempts):
            w1 = self.dictionary.get_random()
            w2 = self.dictionary.get_random()
            
            if not w1 or not w2: 
                return "Словарь пуст."

            result = self._apply_rules(w1, w2)
            if result:
                return result
        
        return "Не удалось подобрать совместимую пару (попробуйте добавить больше текста)."

    def _apply_rules(self, w1: MorphoEntry, w2: MorphoEntry) -> str:
        """Матрица совместимости слов."""
        
        # 1. Прилагательное + Существительное (Red cars)
        if w1.pos == 'ADJ' and w2.pos == 'NOUN':
            # Согласование: используем мн. число существительного
            return f"{w1.lemma} {w2.get_form('plural')} (Adj + Noun)"

        # 2. Существительное + Глагол (Dogs run / Dog runs)
        if w1.pos == 'NOUN' and w2.pos == 'VERB':
            # Согласование: Ед.ч + 3-е лицо
            return f"The {w1.lemma} {w2.get_form('3rd_person')} (Subj + Verb)"

        # 3. Глагол + Существительное (Write code -> Writing codes)
        if w1.pos == 'VERB' and w2.pos == 'NOUN':
            return f"{w1.get_form('gerund')} {w2.get_form('plural')} (Verb + Obj)"
        
        # 4. Глагол + Наречие (Run fast)
        if w1.pos == 'VERB' and w2.pos == 'ADV':
            return f"{w1.lemma} {w2.lemma} (Verb + Adv)"

        # 5. Существительное + Существительное (Data base)
        if w1.pos == 'NOUN' and w2.pos == 'NOUN' and w1.lemma != w2.lemma:
            return f"{w1.lemma} {w2.lemma} (Compound Noun)"

        return None