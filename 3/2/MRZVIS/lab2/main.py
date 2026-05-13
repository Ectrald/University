import random
import math
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional

VALUE_MIN = -1.0
VALUE_MAX = 1.0

IDX_OP3 = 0
IDX_SUM = 1
IDX_IMP = 2
IDX_PROD = 3
IDX_NEG = 4


class InputManager:
    class InputData:
        def __init__(self):
            self.p = 0
            self.m = 0
            self.q = 0
            self.operation_times = [0.0] * 5
            self.seed = 1

    def __init__(self, file_path: str):
        self._file_path = file_path

    def read_from_file(self) -> 'InputManager.InputData':
        with open(self._file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if len(lines) < 3:
            raise Exception("Файл input.txt должен содержать минимум 3 строки")

        data = self.InputData()

        dims = lines[0].split()
        if len(dims) != 3:
            raise Exception("Первая строка должна содержать три числа: p m q")
        
        data.p = int(dims[0])
        data.m = int(dims[1])
        data.q = int(dims[2])
        
        if data.p <= 0 or data.m <= 0 or data.q <= 0:
            raise Exception("Размерности должны быть положительными")

        times = lines[1].split()
        if len(times) != 5:
            raise Exception("Вторая строка должна содержать 5 времён операций")
        
        for i in range(5):
            data.operation_times[i] = float(times[i])

        if len(lines) > 2:
            data.seed = int(lines[2])

        return data


class Operations:
    @staticmethod
    def generate_matrix(rows: int, cols: int, rnd: random.Random) -> List[List[float]]:
        matrix = []
        for i in range(rows):
            row = []
            for j in range(cols):
                row.append(rnd.random() * (VALUE_MAX - VALUE_MIN) + VALUE_MIN)
            matrix.append(row)
        return matrix
    
    @staticmethod
    def generate_vector(length: int, rnd: random.Random) -> List[float]:
        vector = []
        for i in range(length):
            vector.append(rnd.random() * (VALUE_MAX - VALUE_MIN) + VALUE_MIN)
        return vector


class ManualCalculation:
    R_FINAL = 94
    
    def __init__(self, t_imp: float, t_prod: float, t_neg: float, t_sum: float, t_op3: float):
        self.t_imp = t_imp
        self.t_prod = t_prod
        self.t_neg = t_neg
        self.t_sum = t_sum
        self.t_op3 = t_op3
        
        self.l_sum = 0.0
        self.l_avg = 0.0
        
        rnd = random.Random(1)
        p, m, q = 2, 2, 2
        
        self.a = self._generate_matrix(p, m, rnd)
        self.b = self._generate_matrix(m, q, rnd)
        self.e = self._generate_vector(m, rnd)
        self.g = self._generate_matrix(p, q, rnd)
    
    @staticmethod
    def _imp(x: float, y: float) -> float:
        return 1.0 + x * (y - 1.0)
    
    @staticmethod
    def _compose(x: float, y: float) -> float:
        return min(x, y)
    
    @staticmethod
    def _reduce_prod(values: List[float]) -> float:
        result = 1.0
        for v in values:
            result *= v
        return result
    
    @staticmethod
    def _reduce_union(values: List[float]) -> float:
        result = 1.0
        for v in values:
            result *= (1.0 - v)
        return 1.0 - result
    
    @staticmethod
    def _generate_matrix(rows: int, cols: int, rnd: random.Random) -> List[List[float]]:
        m = []
        for i in range(rows):
            row = []
            for j in range(cols):
                row.append(rnd.random() * 2.0 - 1.0)
            m.append(row)
        return m
    
    @staticmethod
    def _generate_vector(length: int, rnd: random.Random) -> List[float]:
        v = []
        for i in range(length):
            v.append(rnd.random() * 2.0 - 1.0)
        return v
    
    def print_matrices(self):
        print("Source matrices:")
        print(f"A =\n{self._format_matrix(self.a)}")
        print(f"B =\n{self._format_matrix(self.b)}")
        print(f"E =\n{self._format_vector(self.e)}")
        print(f"G =\n{self._format_matrix(self.g)}")
    
    @staticmethod
    def _format_matrix(m: List[List[float]]) -> str:
        lines = []
        for row in m:
            line = "  [ "
            for val in row:
                line += f"{val:10.6f} "
            line += "]"
            lines.append(line)
        return "\n".join(lines)
    
    @staticmethod
    def _format_vector(v: List[float]) -> str:
        line = "  [ "
        for val in v:
            line += f"{val:10.6f} "
        line += "]"
        return line
    
    def compute_manual_c00(self) -> float:
        self.l_sum = 0
        self.l_avg = 0
        a, b, e, g = self.a, self.b, self.e, self.g
        
        impl_ab = self._imp(a[0][0], b[0][0])
        impl_ba = self._imp(b[0][0], a[0][0])
        impl_ab_ = self._imp(a[0][1], b[1][0])
        impl_ba_ = self._imp(b[1][0], a[0][1])
        
        d1 = a[0][0] * b[0][0]
        d2 = a[0][1] * b[1][0]
        
        e2_0 = e[0] * 2
        e2_1 = e[1] * 2
        g3 = g[0][0] * 3
        
        e11 = 1 - e[0]
        e12 = 1 - e[1]
        g1 = 1 - g[0][0]
        
        self.l_sum += 4 * self.t_imp + 2 * self.t_prod + 3 * self.t_prod + 3 * self.t_neg
        self.l_avg += (4 * 2 * self.t_imp + 2 * 2 * self.t_prod + 3 * 2 * self.t_prod + 3 * 2 * self.t_neg) / self.R_FINAL
        
        impl_4 = impl_ab * 4
        impl_4_ = impl_ab_ * 4
        e11_2_1 = e2_0 - 1
        e12_2_1 = e2_1 - 1
        d1_1 = 1 - d1
        d2_1 = 1 - d2
        g_32 = g3 - 2
        
        self.l_sum += 2 * self.t_prod + 5 * self.t_neg
        self.l_avg += (2 * 3 * self.t_prod + 5 * 3 * self.t_neg) / self.R_FINAL
        
        impl_4_2 = impl_4 - 2
        impl_4_2_ = impl_4_ - 2
        ab_e11 = e11_2_1 * impl_ab
        ab_e11_ = e12_2_1 * impl_ab_
        pk = d1_1 * d2_1
        gg_32 = g_32 * g[0][0]
        
        self.l_sum += 2 * self.t_neg + 4 * self.t_prod
        self.l_avg += (2 * 4 * self.t_neg + (2 * 5 + 1 * 6 + 1 * 4) * self.t_prod) / self.R_FINAL
        
        temp1 = e[0] * impl_4_2
        temp2 = e[1] * impl_4_2_
        d11 = 1 - pk
        
        self.l_sum += 2 * self.t_prod + self.t_neg
        self.l_avg += (2 * 5 * self.t_prod + 1 * 7 * self.t_neg) / self.R_FINAL
        
        temp1_1 = temp1 + 1
        temp2_1 = temp2 + 1
        part1_1 = ab_e11 * e[0]
        part1_2 = ab_e11_ * e[1]
        d11_3 = d11 * 3
        
        self.l_sum += 2 * self.t_sum + 3 * self.t_prod
        self.l_avg += (2 * 6 * self.t_sum + (2 * 6 + 1 * 8) * self.t_prod) / self.R_FINAL
        
        temp = impl_ba * temp1_1
        temp_ = impl_ba_ * temp2_1
        
        self.l_sum += 2 * self.t_prod
        self.l_avg += (2 * 8 * self.t_prod) / self.R_FINAL
        
        part2_1 = temp * e11
        part2_2 = temp_ * e12
        
        self.l_sum += 2 * self.t_prod
        self.l_avg += (2 * 10 * self.t_prod) / self.R_FINAL
        
        f111 = part2_1 + part1_1
        f112 = part2_2 + part1_2
        
        self.l_sum += 2 * self.t_sum
        self.l_avg += (2 * 16 * self.t_sum) / self.R_FINAL
        
        f_prod = f111 * f112
        
        self.l_sum += self.t_prod
        self.l_avg += (self.t_prod * 32) / self.R_FINAL
        
        df = self._compose(d11, f_prod)
        part_c_1 = gg_32 * f_prod
        
        self.l_sum += self.t_op3 + self.t_prod
        self.l_avg += (39 * self.t_op3 + 36 * self.t_prod) / self.R_FINAL
        
        df4 = df * 4
        
        self.l_sum += self.t_prod
        self.l_avg += (40 * self.t_prod) / self.R_FINAL
        
        dd4 = df4 - d11_3
        
        self.l_sum += self.t_neg
        self.l_avg += (48 * self.t_neg) / self.R_FINAL
        
        dd4g = dd4 * g[0][0]
        
        self.l_sum += self.t_prod
        self.l_avg += (49 * self.t_prod) / self.R_FINAL
        
        ddd4g = dd4g + d11
        
        self.l_sum += self.t_sum
        self.l_avg += (56 * self.t_sum) / self.R_FINAL
        
        part_c_2 = ddd4g * g1
        
        self.l_sum += self.t_prod
        self.l_avg += (self.t_prod * 58) / self.R_FINAL
        
        c11 = part_c_2 + part_c_1
        
        self.l_sum += self.t_sum
        self.l_avg += (self.t_sum * 94) / self.R_FINAL
        
        return c11
    
    def compute_full_c(self) -> List[List[float]]:
        p = len(self.a)
        q = len(self.b[0])
        m = len(self.a[0])
        c = [[0.0] * q for _ in range(p)]
        
        for i in range(p):
            for j in range(q):
                f_list = []
                d_list = []
                
                for k in range(m):
                    a_val = self.a[i][k]
                    b_val = self.b[k][j]
                    e_val = self.e[k]
                    
                    d_temp = a_val * b_val
                    d_list.append(d_temp)
                    
                    imp_ab = self._imp(a_val, b_val)
                    imp_ba = self._imp(b_val, a_val)
                    
                    term1 = imp_ab * (2 * e_val - 1) * e_val
                    term2 = imp_ba * (1 + (4 * imp_ab - 2) * e_val) * (1 - e_val)
                    f_list.append(term1 + term2)
                
                f = self._reduce_prod(f_list)
                d = self._reduce_union(d_list)
                
                comb = self._compose(f, d)
                
                g_val = self.g[i][j]
                term_a = f * (3 * g_val - 2) * g_val
                term_b = (1 - g_val) * (d + (4 * comb - 3 * d) * g_val)
                c[i][j] = term_a + term_b
        
        return c
    
    def print_results(self, c11_manual: float):
        print("Result:")
        c = self.compute_full_c()
        print("Matrix C:")
        print(self._format_matrix(c))
        print(f"\nC_11 = {c11_manual}")
        print(f"L_sum = {self.l_sum}")
        print(f"L_avg = {self.l_avg}")
        
        d_val = self.l_sum / self.l_avg if self.l_avg > 0 else 0
        print(f"D = {d_val:.3f}")
        
        c11_full = c[0][0]
        diff = abs(c11_manual - c11_full)
        print(f"\nVerification: C[0,0] from compute_full_c = {c11_full}")
        status = "OK" if diff < 1e-10 else "FAIL"
        print(f"Difference: {diff:.2e} {status}")


class MetricsCalculator:
    @staticmethod
    def calculate(n1: int, n2: int, max_r: int, op_times: List[float]) -> Tuple[List[float], List[float], List[float]]:
        ranks = []
        speedup = []
        efficiency = []
        
        for size in range(1, max_r + 1):
            p = m = q = size
            r = MetricsCalculator._compute_rank(p, q, m)
            ranks.append(r)
            
            k1, e1 = MetricsCalculator._compute_metrics(p, q, m, n1, op_times)
            k2, e2 = MetricsCalculator._compute_metrics(p, q, m, n2, op_times)
            
            speedup.append((k1 + k2) / 2)
            efficiency.append((e1 + e2) / 2)
        
        return ranks, speedup, efficiency
    
    @staticmethod
    def calculate_vs_n(target_r: int, max_n: int, op_times: List[float]) -> Tuple[List[float], List[float], List[float]]:
        n_vals = [float(x) for x in range(1, max_n + 1)]
        speedup = [0.0] * max_n
        efficiency = [0.0] * max_n
        
        p, q, m = MetricsCalculator._find_params_for_rank(target_r)
        if p == 0:
            return n_vals, speedup, efficiency
        
        for i in range(max_n):
            n = i + 1
            ky, eff = MetricsCalculator._compute_metrics(p, q, m, n, op_times)
            speedup[i] = ky
            efficiency[i] = eff
        
        return n_vals, speedup, efficiency
    
    @staticmethod
    def _compute_rank(p: int, q: int, m: int) -> float:
        return p * q + q * m + p * m + m + p * q
    
    @staticmethod
    def _find_params_for_rank(target_r: int, max_val: int = 15) -> Tuple[int, int, int]:
        for p in range(1, max_val + 1):
            for q in range(1, max_val + 1):
                for m in range(1, max_val + 1):
                    if MetricsCalculator._compute_rank(p, q, m) == target_r:
                        return p, q, m
        return 0, 0, 0
    
    @staticmethod
    def _compute_metrics(p: int, q: int, m: int, n: int, op_times: List[float]) -> Tuple[float, float]:
        ops_per_element = m * (2 * op_times[IDX_IMP] + 8 * op_times[IDX_PROD] + 
                               3 * op_times[IDX_NEG] + 2 * op_times[IDX_SUM]) + \
                         (2 * m - 1) * op_times[IDX_PROD] + (m + 1) * op_times[IDX_NEG] + \
                         op_times[IDX_OP3] + 7 * op_times[IDX_PROD] + \
                         3 * op_times[IDX_NEG] + 2 * op_times[IDX_SUM]
        
        t1 = p * q * ops_per_element
        
        t_n = t1 / n + math.ceil(math.log2(max(m, 2))) * op_times[IDX_PROD]
        
        ky = t1 / max(t_n, 1e-9)
        eff = ky / n
        
        eff = min(eff, 1.0)
        
        return ky, eff


class GraphicsBuilder:
    def __init__(self, t_imp: float, t_prod: float, t_neg: float, t_sum: float, t_op3: float):
        self.t_imp = t_imp
        self.t_prod = t_prod
        self.t_neg = t_neg
        self.t_sum = t_sum
        self.t_op3 = t_op3
        self.rnd = random.Random(42)
        
        self.cnt_imp = 0
        self.cnt_prod = 0
        self.cnt_neg = 0
        self.cnt_sum = 0
        self.cnt_op3 = 0
    
    def _reset_counters(self):
        self.cnt_imp = 0
        self.cnt_prod = 0
        self.cnt_neg = 0
        self.cnt_sum = 0
        self.cnt_op3 = 0
    
    def _imp_counted(self, x: float, y: float) -> float:
        self.cnt_imp += 1
        if abs(1.0 - x) < 1e-9:
            return y if y >= 0 else -1.0
        return max(-1.0, min(1.0, y / (1.0 - x)))
    
    def _mult(self, a: float, b: float) -> float:
        self.cnt_prod += 1
        return a * b
    
    def _sub(self, a: float, b: float) -> float:
        self.cnt_neg += 1
        return a - b
    
    def _add(self, a: float, b: float) -> float:
        self.cnt_sum += 1
        return a + b
    
    def _compose(self, a: float, b: float) -> float:
        self.cnt_op3 += 1
        return a * b
    
    def _fill_matrix(self, m: int, p: int, q: int):
        a = [[round(self.rnd.random() * 2.001 - 1.0, 3) for _ in range(m)] for _ in range(p)]
        b = [[round(self.rnd.random() * 2.001 - 1.0, 3) for _ in range(q)] for _ in range(m)]
        e = [[round(self.rnd.random() * 2.001 - 1.0, 3) for _ in range(m)]]
        g = [[round(self.rnd.random() * 2.001 - 1.0, 3) for _ in range(q)] for _ in range(p)]
        return a, b, e, g
    
    def _compute_r(self, p: int, q: int, m: int) -> float:
        return p * q + q * m + p * m + m + p * q
    
    def _compute_tavg(self, p: int, q: int, m: int) -> float:
        per_ij = 0.0
        per_ij += m * (2 * self.t_imp + 8 * self.t_prod + 3 * self.t_neg + 2 * self.t_sum)
        per_ij += (2 * m - 2) * self.t_prod + (m + 1) * self.t_neg
        per_ij += self.t_op3 + 7 * self.t_prod + 3 * self.t_neg + 2 * self.t_sum
        return p * q * per_ij
    
    def compute_metrics(self, p: int, q: int, m: int, n: int) -> Tuple[float, float, float, float]:
        self._reset_counters()
        t_n = 0.0
        a, b, e, g = self._fill_matrix(m, p, q)
        
        for i in range(p):
            for j in range(q):
                f_list = []
                d_list = []
                old_tn = t_n
                
                for k in range(m):
                    a_val = a[i][k]
                    b_val = b[k][j]
                    e_val = e[0][k]
                    d_list.append(self._compose(a_val, b_val))
                    
                    imp_ab = self._imp_counted(a_val, b_val)
                    imp_ba = self._imp_counted(b_val, a_val)
                    
                    term1 = self._mult(self._mult(imp_ab, self._sub(self._mult(2, e_val), 1)), e_val)
                    term2 = self._mult(self._mult(imp_ba, self._add(1, self._mult(self._sub(self._mult(4, imp_ab), 2), e_val))), self._sub(1, e_val))
                    f_list.append(self._add(term1, term2))
                    
                    t_n += math.ceil(1.0 / n) * self.t_op3
                    t_n += math.ceil(7.0 / n) * self.t_prod
                    t_n += math.ceil(2.0 / n) * self.t_imp
                    t_n += math.ceil(3.0 / n) * self.t_neg
                    t_n += math.ceil(2.0 / n) * self.t_sum
                
                if 6 <= n <= m * 3:
                    new_n = n - n % 3
                    count = math.ceil((m * 3.0) / new_n)
                    temp = (t_n - old_tn) / m
                    t_n -= (m - count) * temp
                elif n >= m * 3:
                    temp = (t_n - old_tn) / m
                    t_n = old_tn + temp
                
                prod_f = f_list[0]
                for idx in range(1, len(f_list)):
                    prod_f = self._mult(prod_f, f_list[idx])
                t_n += math.ceil((m - 1.0) / n) * self.t_prod
                
                d1min = [self._sub(1, d) for d in d_list]
                dd = d1min[0]
                for idx in range(1, len(d1min)):
                    dd = self._mult(dd, d1min[idx])
                d_ij = self._sub(1, dd)
                t_n += math.ceil(float(m) / n) * self.t_neg
                t_n += math.ceil((m - 1.0) / n) * self.t_prod
                t_n += self.t_neg
                
                comb = self._compose(prod_f, d_ij)
                t_n += math.ceil(1.0 / n) * self.t_op3
                
                g_val = g[i][j]
                term_a = self._mult(self._mult(prod_f, self._sub(self._mult(3, g_val), 2)), g_val)
                term_b = self._mult(self._sub(1, g_val), self._add(d_ij, self._mult(self._sub(self._mult(4, comb), self._mult(3, d_ij)), g_val)))
                self._add(term_a, term_b)
                
                t_n += math.ceil(7.0 / n) * self.t_prod
                t_n += math.ceil(3.0 / n) * self.t_neg
                t_n += math.ceil(2.0 / n) * self.t_sum
        
        t1 = self.cnt_imp * self.t_imp + self.cnt_prod * self.t_prod + self.cnt_neg * self.t_neg + self.cnt_sum * self.t_sum + self.cnt_op3 * self.t_op3
        r_val = self._compute_r(p, q, m)
        t_avg = self._compute_tavg(p, q, m)
        l_avg = t_avg / r_val if r_val > 0 else 1
        t_n = max(t_n, 1e-9)
        
        ky = t1 / t_n
        eff = ky / n
        d_val = t_n / l_avg if l_avg > 0 else 0
        
        return ky, eff, d_val, r_val
    
    def find_params_for_r(self, target_r: int, max_val: int = 15) -> Tuple[int, int, int]:
        for p in range(1, max_val + 1):
            for q in range(1, max_val + 1):
                for m in range(1, max_val + 1):
                    if self._compute_r(p, q, m) == target_r:
                        return p, q, m
        return 0, 0, 0
    
    def _save_plot(self, x, y1, y2, xl, yl, title, l1, l2, fname, dir_path):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, y1, label=l1, linewidth=2, marker='o', markersize=5)
        ax.plot(x, y2, label=l2, linewidth=2, marker='s', markersize=5)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_title(title)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        path = os.path.join(dir_path, fname)
        fig.savefig(path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        print(f"  -> Saved: {path}")
    
    def build(self, output_dir: str = "plots"):
        os.makedirs(output_dir, exist_ok=True)
        print("\n" + "=" * 70)
        print("BUILDING PLOTS")
        print("=" * 70)
        
        r_vals = []
        ky_n8 = []
        ky_n10 = []
        eff_n8 = []
        eff_n10 = []
        d_n8 = []
        d_n10 = []
        
        for size in range(1, 21):
            p = q = m = size
            r_vals.append(self._compute_r(p, q, m))
            
            k4, e4, d4, _ = self.compute_metrics(p, q, m, n=4)
            k8, e8, d8, _ = self.compute_metrics(p, q, m, n=8)
            
            ky_n8.append(k4)
            ky_n10.append(k8)
            eff_n8.append(e4)
            eff_n10.append(e8)
            d_n8.append(d4)
            d_n10.append(d8)
        
        self._save_plot(r_vals, ky_n8, ky_n10,
                        "Task rank (r)", "Speedup (Ky)",
                        "Ky vs r", "n = 4", "n = 8", "Ky_vs_r.png", output_dir)
        
        self._save_plot(r_vals, eff_n8, eff_n10,
                        "Task rank (r)", "Efficiency (e)",
                        "Efficiency vs r", "n = 4", "n = 8", "Eff_vs_r.png", output_dir)
        
        self._save_plot(r_vals, d_n8, d_n10,
                        "Task rank (r)", "Deviation (D)",
                        "D vs r", "n = 4", "n = 8", "D_vs_r.png", output_dir)
        
        p32 = self.find_params_for_r(32)
        p64 = self.find_params_for_r(64)
        
        if p32[0] != 0 and p64[0] != 0:
            n_max = 51
            n_vals = [float(x) for x in range(1, n_max)]
            ky32 = [0.0] * (n_max - 1)
            ky48 = [0.0] * (n_max - 1)
            eff32 = [0.0] * (n_max - 1)
            eff48 = [0.0] * (n_max - 1)
            d32 = [0.0] * (n_max - 1)
            d48 = [0.0] * (n_max - 1)
            
            for n in range(1, n_max):
                k32, e32, d32v, _ = self.compute_metrics(p32[0], p32[1], p32[2], n)
                k48, e48, d48v, _ = self.compute_metrics(p64[0], p64[1], p64[2], n)
                
                ky32[n - 1] = k32
                ky48[n - 1] = k48
                eff32[n - 1] = e32
                eff48[n - 1] = e48
                d32[n - 1] = d32v
                d48[n - 1] = d48v
            
            self._save_plot(n_vals, ky32, ky48,
                            "PE count (n)", "Ky",
                            "Ky vs n", "r = 32", "r = 64", "Ky_vs_n.png", output_dir)
            
            self._save_plot(n_vals, eff32, eff48,
                            "PE count (n)", "e",
                            "Efficiency vs n", "r = 32", "r = 64", "Eff_vs_n.png", output_dir)
            
            self._save_plot(n_vals, d32, d48,
                            "PE count (n)", "D",
                            "D vs n", "r = 32", "r = 64", "D_vs_n.png", output_dir)
        
        print("\nAll 6 plots built.")


def main():
    print("=" * 70)
    print("Lab2: OKMD architecture - Variant 7")
    print("(~) = min,  /~\\ = *,  x~>y = 1+x*(y-1)")
    print("=" * 70 + "\n")
    
    input_mgr = InputManager("input.txt")
    input_data = input_mgr.read_from_file()
    
    print(f"Parameters: p={input_data.p}, m={input_data.m}, q={input_data.q}")
    print(f"Times: op3={input_data.operation_times[0]}, sum={input_data.operation_times[1]}, "
          f"imp={input_data.operation_times[2]}, prod={input_data.operation_times[3]}, neg={input_data.operation_times[4]}")
    print(f"Seed: {input_data.seed}\n")
    
    rnd = random.Random(input_data.seed)
    a = Operations.generate_matrix(input_data.p, input_data.m, rnd)
    b = Operations.generate_matrix(input_data.m, input_data.q, rnd)
    e = Operations.generate_vector(input_data.m, rnd)
    g = Operations.generate_matrix(input_data.p, input_data.q, rnd)
    
    manual = ManualCalculation(
        t_imp=input_data.operation_times[0],
        t_prod=input_data.operation_times[1],
        t_neg=input_data.operation_times[2],
        t_sum=input_data.operation_times[3],
        t_op3=input_data.operation_times[4]
    )
    
    manual.print_matrices()
    
    c11 = manual.compute_manual_c00()
    manual.print_results(c11)
    
    builder = GraphicsBuilder(t_imp=10, t_prod=5, t_neg=3, t_sum=2, t_op3=8)
    builder.build("plots")


if __name__ == "__main__":
    main()