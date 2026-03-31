import urllib.request
import json
import os

os.makedirs('diagrams', exist_ok=True)

def generate_plantuml_block_scheme(puml_code, filename):
    url = 'https://kroki.io/plantuml/png'
    data = {
        'diagram_source': puml_code
    }
    encoded_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded_data, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            with open(os.path.join('diagrams', filename), 'wb') as f:
                f.write(response.read())
        print(f"Generated {filename}")
    except Exception as e:
        print(f"Failed to generate {filename}: {e}")

common_skinparam = """
skinparam linetype ortho
skinparam ActivityShape octagon
skinparam ConditionEndStyle hline
skinparam DefaultFontName Arial
skinparam ActivityBackgroundColor white
skinparam ActivityBorderColor black
skinparam ConditionBackgroundColor white
skinparam ConditionBorderColor black
skinparam ArrowColor black
"""

flowcharts = {}

flowcharts['main_main.png'] = f'''@startuml
{common_skinparam}
start
:app = CLI();
:app.run();
if (KeyboardInterrupt?) then (Да)
  :Вывод: 'Выход из программы';
else (Норм. завершение)
endif
stop
@enduml'''

flowcharts['stage_init.png'] = f'''@startuml
{common_skinparam}
start
:self.idx = stage_idx\\nself.cycles_required = cycles_required\\nИнициализация полей (0, None, False);
stop
@enduml'''

flowcharts['simulation_init.png'] = f'''@startuml
{common_skinparam}
start
:self.p = p, self.n = n\\nself.queue = queue\\nself.tact = 0;
while (Для i, t в stage_times) is (Итерация)
  :Добавить Stage(i, t)\\nв self.stages;
endwhile (Конец списка)
:self.results = пустой список\\nself.ky = 0.0\\nself.eff = 0.0;
stop
@enduml'''

flowcharts['simulation_save_state.png'] = f'''@startuml
{common_skinparam}
start
:state = tact, queue, results;
while (Для s в self.stages) is (Итерация)
  :Сохранить состояние этапа s\\nв state;
endwhile (Конец списка)
:self.history.append(state);
stop
@enduml'''

flowcharts['simulation_load_state.png'] = f'''@startuml
{common_skinparam}
start
if (not self.history?) then (Да)
  stop
else (Нет)
endif
:state = self.history.pop()\\nВосстановление tact, queue, results;
while (Для i, data в state) is (Итерация)
  :Восстановление \\nсостояния этапов\\nself.stages[i] из data;
endwhile (Конец списка)
stop
@enduml'''

flowcharts['simulation_process_stage.png'] = f'''@startuml
{common_skinparam}
start
if (s.current_pair is None?) then (Да)
  stop
else (Нет)
endif
:a, b = s.current_pair\\nВычисление end_bit;
while (bit_idx от s.current_bit_idx до end_bit) is (Итерация)
  if (Бит a[bit_idx] == 1?) then (Да)
    :s.partial_result +=\\nb << bit_idx;
  else (Нет)
  endif
endwhile (Конец цикла)
:s.bits_processed = end_bit\\ns.current_bit_idx = end_bit;
stop
@enduml'''

flowcharts['simulation_next_tact.png'] = f'''@startuml
{common_skinparam}
start
:self.save_state()\\nself.tact += 1;
while (Для s в stages) is (Итерация)
  :Уменьшение s.cycles_left;
endwhile (Конец)

while (Для i = n-1 down to 0) is (Итерация)
  if (Этап завершил цикл?) then (Да)
    if (i == n-1 ?) then (Да)
      :Пара переходит\\nв self.results;
    else (Нет)
      :Пара переходит\\nна i+1 этап;
    endif
  else (Нет)
  endif
endwhile (Конец)

while (Для s в stages) is (Итерация)
  if (s.cycles_left > 0?) then (Да)
    :process_stage(s);
  else (Нет)
  endif
endwhile (Конец)

if (Очередь не пуста и\\nЭтап 0 свободен?) then (Да)
  :Пара из queue\\nпоступает на Этап 0;
else (Нет)
endif
stop
@enduml'''

flowcharts['simulation_calculate_metrics.png'] = f'''@startuml
{common_skinparam}
start
:t1 = self.m * self.p\\ntn = self.tact - 1;
if (tn > 0 ?) then (Да)
  :self.ky = t1 / tn\\nself.eff = self.ky / self.n;
else (Нет)
endif
stop
@enduml'''

flowcharts['cli_init.png'] = f'''@startuml
{common_skinparam}
start
:self.n = 0\\nself.p = 0\\nself.queue = пустой список\\nself.sim = None;
stop
@enduml'''

flowcharts['cli_display_simulation.png'] = f'''@startuml
{common_skinparam}
start
:Очистка консоли (clear_console);
:Вывод текущего такта;
:Вывод элементов очереди;
while (Для s в self.stages) is (Итерация)
  :Вывод состояния этапа s;
endwhile (Конец)
:Вывод обработанных результатов;
:Вывод меню управления;
stop
@enduml'''

flowcharts['cli_run.png'] = f'''@startuml
{common_skinparam}
start
:Ввод p, n, m\\nВвод times;
:Режим ввода: random / manual?;
:sim = Simulation(...);
while (Бесконечный цикл) is (while True)
  :self.display_simulation();
  :Ввод команды (1, 2 или 3);
  
  if (Команда 1: Вперед?) then (Да)
     if (Все пары готовы?) then (Да)
       break
     else (Нет)
       :sim.next_tact();
     endif
  elseif (Команда 2: Назад?) then (Да)
     :sim.load_state();
  elseif (Команда 3: Промотать?) then (Да)
     :Быстрая промотка\\nдо конца;
     break
  else (Ошибка ввода)
  endif
endwhile (break)
:Вывод метрик Ky, Eff;
if (Построить графики?) then (Да)
  :plot_metrics(...);
else (Нет)
endif
stop
@enduml'''

flowcharts['metrics_run_full_simulation.png'] = f'''@startuml
{common_skinparam}
start
:sim = Simulation(p,n,queue,times);
while (Очередь не пуста или этапы заняты?) is (Да)
  :sim.next_tact();
endwhile (Нет)
:sim.calculate_metrics();
:Возврат sim;
stop
@enduml'''

flowcharts['metrics_plot_metrics.png'] = f'''@startuml
{common_skinparam}
start
:kys=пустой_список, effs=пустой_список\\nms = 1..max_m;
while (Для m in ms) is (Итерация)
  :sim = run_full_simulation(m)\\nДобавить ky, eff в списки;
endwhile (Конец)
:Отрисовка subplot(kys)\\nОтрисовка subplot(effs)\\nplt.show();
stop
@enduml'''

flowcharts['helpers_clear_console.png'] = f'''@startuml
{common_skinparam}
start
if (os.name == 'nt'?) then (Да)
  :os.system('cls');
else (Нет)
  :os.system('clear');
endif
stop
@enduml'''

flowcharts['helpers_format_bin.png'] = f'''@startuml
{common_skinparam}
start
:Округление bits_needed до\\nкратного 4 (total_len);
:Форматирование value в\\nдвоичную строку с нулями;
:Разбиение строки\\nна группы по 4 разряда;
:Возврат результата;
stop
@enduml'''

for name, puml in flowcharts.items():
    generate_plantuml_block_scheme(puml, name)

print("PlantUML flowcharts successfully generated.")
