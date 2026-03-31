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
    def __init__(self, p, n, queue, stage_times):
        self.p = p
        self.n = n
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
            'queue': [dict(p_item) for p_item in self.queue],
            'results': list(self.results),
            'stages_data': []
        }
        for s in self.stages:
            state['stages_data'].append({
                'pair': dict(s.current_pair) if s.current_pair else None,
                'cycles_left': s.cycles_left,
                'bits_processed': s.bits_processed,
                'partial_result': s.partial_result,
                'current_bit_idx': s.current_bit_idx
            })
        self.history.append(state)

    def load_state(self):
        if not self.history: return
        state = self.history.pop()
        self.tact, self.queue, self.results = state['tact'], state['queue'], state['results']
        for i, data in enumerate(state['stages_data']):
            self.stages[i].current_pair = data['pair']
            self.stages[i].cycles_left = data['cycles_left']
            self.stages[i].bits_processed = data['bits_processed']
            self.stages[i].partial_result = data['partial_result']
            self.stages[i].current_bit_idx = data['current_bit_idx']

    def process_stage(self, s):
        if s.current_pair is None: return
        a, b = s.current_pair['a'], s.current_pair['b']
        bits_per_stage = (self.p + self.n - 1) // self.n
        end_bit = min(s.current_bit_idx + bits_per_stage, self.p)
        for bit_idx in range(s.current_bit_idx, end_bit):
            if (a >> bit_idx) & 1:
                s.partial_result += b << bit_idx
        s.bits_processed = end_bit
        s.current_bit_idx = end_bit

    def next_tact(self):
        self.save_state()
        self.tact += 1
        
        for s in self.stages:
            if s.current_pair:
                s.cycles_left -= 1

        for i in range(self.n - 1, -1, -1):
            s = self.stages[i]
            if s.current_pair and s.cycles_left <= 0:
                if s.current_bit_idx >= self.p:
                    if i == self.n - 1:
                        self.results.append({
                            'id': s.current_pair['id'],
                            'result': s.partial_result,
                            'completed_tact': self.tact - 1
                        })
                        s.current_pair = None
                    else:
                        next_s = self.stages[i + 1]
                        if next_s.current_pair is None:
                            next_s.current_pair = s.current_pair
                            next_s.cycles_left = next_s.cycles_required
                            next_s.bits_processed = s.bits_processed
                            next_s.partial_result = s.partial_result
                            next_s.current_bit_idx = s.current_bit_idx
                            s.current_pair = None

        for s in self.stages:
            if s.current_pair and s.cycles_left > 0:
                self.process_stage(s)

        if self.queue and self.stages[0].current_pair is None:
            pair = self.queue.pop(0)
            s = self.stages[0]
            s.current_pair = pair
            s.cycles_left = s.cycles_required
            s.bits_processed = 0
            s.partial_result = 0
            s.current_bit_idx = 0
            self.process_stage(s)

    def calculate_metrics(self):
        t1 = self.m * self.p
        tn = self.tact - 1
        if tn > 0:
            self.ky = t1 / tn
            self.eff = self.ky / self.n
