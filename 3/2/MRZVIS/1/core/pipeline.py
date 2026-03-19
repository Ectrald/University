"""
//////////////////
Лабораторная работа No1 по дисциплине МРЗвИС
Выполнена студентом группы 321701 БГУИР Германенко Владислав Вадимович
Файл: Модель конвейера и симуляции циклов
!! 18.03.2026
[Основано на лекционном материале, алгоритм умножения с младших разрядов со сдвигом влево]
//////////////////
"""
from core.stage import Stage

class Simulation:
    def __init__(self, p, queue, stage_times):
        self.p = p
        self.queue = queue
        self.m = len(queue)
        self.stage_times = stage_times
        self.tact = 0
        self.stages = [Stage(i, t) for i, t in enumerate(stage_times)]
        self.results = []
        self.history = []

        self.ky = 0.0
        self.eff = 0.0

    def save_state(self):
        state = {
            'tact': self.tact,
            'queue': [dict(p) for p in self.queue],
            'results': list(self.results),
            'stages_data': []
        }
        for s in self.stages:
            state['stages_data'].append({
                'pair': dict(s.current_pair) if s.current_pair else None,
                'cycles_left': s.cycles_left,
                'p_sum': s.p_sum,
                'p_prod': s.p_prod
            })
        self.history.append(state)

    def load_state(self):
        if not self.history: return
        state = self.history.pop()
        self.tact, self.queue, self.results = state['tact'], state['queue'], state['results']
        for i, data in enumerate(state['stages_data']):
            self.stages[i].current_pair, self.stages[i].cycles_left = data['pair'], data['cycles_left']
            self.stages[i].p_sum, self.stages[i].p_prod = data['p_sum'], data['p_prod']

    def next_tact(self):
        self.save_state()
        self.tact += 1
        for s in self.stages:
            if s.current_pair: s.cycles_left -= 1

        for i in range(self.p - 1, -1, -1):
            s = self.stages[i]
            if s.current_pair and s.cycles_left <= 0:
                if i == self.p - 1:
                    self.results.append(
                        {'id': s.current_pair['id'], 'result': s.p_sum, 'completed_tact': self.tact - 1})
                    s.current_pair = None
                else:
                    next_s = self.stages[i + 1]
                    if next_s.current_pair is None:
                        pair = s.current_pair
                        bit = (pair['a'] >> (i + 1)) & 1
                        prod = (pair['b'] << (i + 1)) if bit else 0
                        next_s.current_pair, next_s.cycles_left = pair, next_s.cycles_required
                        next_s.p_prod, next_s.p_sum = prod, s.p_sum + prod
                        s.current_pair = None

        if self.queue and self.stages[0].current_pair is None:
            pair = self.queue.pop(0)
            s = self.stages[0]
            bit = (pair['a'] >> 0) & 1
            prod = pair['b'] if bit else 0
            s.current_pair, s.cycles_left = pair, s.cycles_required
            s.p_prod, s.p_sum = prod, prod

    def calculate_metrics(self):
        t1 = self.m * sum(self.stage_times)
        tn = self.tact - 1
        if tn > 0:
            self.ky = t1 / tn
            self.eff = self.ky / self.p
