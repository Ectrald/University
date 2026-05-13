using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ScottPlot;

namespace Lab2_OKMD.Visualization
{
    /// <summary>
    /// Генератор графиков производительности для ОКМД-архитектуры.
    /// Полностью повторяет логику Python-класса GraphicsBuilder с использованием ScottPlot.
    /// </summary>
    public class GraphicsBuilder
    {
        private readonly double _tImp;
        private readonly double _tProd;
        private readonly double _tNeg;
        private readonly double _tSum;
        private readonly double _tOp3;
        private readonly Random _rnd;

        // Счётчики операций
        private int _cntImp, _cntProd, _cntNeg, _cntSum, _cntOp3;

        public GraphicsBuilder(double tImp, double tProd, double tNeg, double tSum, double tOp3)
        {
            _tImp = tImp; _tProd = tProd; _tNeg = tNeg; _tSum = tSum; _tOp3 = tOp3;
            _rnd = new Random(42);
        }

        #region Вспомогательные методы операций

        private void ResetCounters() => _cntImp = _cntProd = _cntNeg = _cntSum = _cntOp3 = 0;

        private double ImpCounted(double x, double y)
        {
            _cntImp++;
            if (Math.Abs(1.0 - x) < 1e-9) return y >= 0 ? 1.0 : -1.0;
            return Math.Max(-1.0, Math.Min(1.0, y / (1.0 - x)));
        }

        private double Mult(double a, double b) { _cntProd++; return a * b; }
        private double Sub(double a, double b) { _cntNeg++; return a - b; }
        private double Add(double a, double b) { _cntSum++; return a + b; }
        private double Compose(double a, double b) { _cntOp3++; return a * b; } // В Python: _compose считает как op3, но возвращает произведение

        #endregion

        #region Генерация данных

        private (double[][] A, double[][] B, double[][] E, double[][] G) FillMatrix(int m, int p, int q)
        {
            double[][] A = new double[p][];
            double[][] B = new double[m][];
            double[][] E = new double[1][];
            double[][] G = new double[p][];

            for (int i = 0; i < p; i++) A[i] = Enumerable.Range(0, m).Select(_ => Math.Round(_rnd.NextDouble() * 2.001 - 1.0, 3)).ToArray();
            for (int i = 0; i < m; i++) B[i] = Enumerable.Range(0, q).Select(_ => Math.Round(_rnd.NextDouble() * 2.001 - 1.0, 3)).ToArray();
            E[0] = Enumerable.Range(0, m).Select(_ => Math.Round(_rnd.NextDouble() * 2.001 - 1.0, 3)).ToArray();
            for (int i = 0; i < p; i++) G[i] = Enumerable.Range(0, q).Select(_ => Math.Round(_rnd.NextDouble() * 2.001 - 1.0, 3)).ToArray();

            return (A, B, E, G);
        }

        private double ComputeR(int p, int q, int m) => p * q + q * m + p * m + m + p * q;

        private double ComputeTavg(int p, int q, int m)
        {
            double perIj = 0.0;
            perIj += m * (2 * _tImp + 8 * _tProd + 3 * _tNeg + 2 * _tSum);
            perIj += (2 * m - 2) * _tProd + (m + 1) * _tNeg;
            perIj += _tOp3 + 7 * _tProd + 3 * _tNeg + 2 * _tSum;
            return p * q * perIj;
        }

        #endregion

        public (double Ky, double Eff, double D, double RVal) ComputeMetrics(int p, int q, int m, int n)
        {
            ResetCounters();
            double Tn = 0.0;
            var (A, B, E, G) = FillMatrix(m, p, q);

            for (int i = 0; i < p; i++)
            {
                for (int j = 0; j < q; j++)
                {
                    var fList = new List<double>();
                    var dList = new List<double>();
                    double oldTn = Tn;

                    for (int k = 0; k < m; k++)
                    {
                        double a = A[i][k], b = B[k][j], e = E[0][k];
                        dList.Add(Compose(a, b));

                        double impAB = ImpCounted(a, b);
                        double impBA = ImpCounted(b, a);

                        double term1 = Mult(Mult(impAB, Sub(Mult(2, e), 1)), e);
                        double term2 = Mult(Mult(impBA, Add(1, Mult(Sub(Mult(4, impAB), 2), e))), Sub(1, e));
                        fList.Add(Add(term1, term2));

                        // Группированный параллельный учёт
                        Tn += Math.Ceiling(1.0 / n) * _tOp3;
                        Tn += Math.Ceiling(7.0 / n) * _tProd;
                        Tn += Math.Ceiling(2.0 / n) * _tImp;
                        Tn += Math.Ceiling(3.0 / n) * _tNeg;
                        Tn += Math.Ceiling(2.0 / n) * _tSum;
                    }

                    // Эвристика насыщения конвейера
                    if (6 <= n && n <= m * 3)
                    {
                        int newN = n - n % 3;
                        int count = (int)Math.Ceiling((m * 3.0) / newN);
                        double temp = (Tn - oldTn) / m;
                        Tn -= (m - count) * temp;
                    }
                    else if (n >= m * 3)
                    {
                        double temp = (Tn - oldTn) / m;
                        Tn = oldTn + temp;
                    }

                    // prod_over_k
                    double prodF = fList[0];
                    for (int idx = 1; idx < fList.Count; idx++) prodF = Mult(prodF, fList[idx]);
                    Tn += Math.Ceiling((m - 1.0) / n) * _tProd;

                    // union_over_k
                    var d1min = new List<double>();
                    foreach (var d in dList) d1min.Add(Sub(1, d));
                    double dd = d1min[0];
                    for (int idx = 1; idx < d1min.Count; idx++) dd = Mult(dd, d1min[idx]);
                    double dIj = Sub(1, dd);
                    Tn += Math.Ceiling((double)m / n) * _tNeg;
                    Tn += Math.Ceiling((m - 1.0) / n) * _tProd;
                    Tn += _tNeg;

                    // binary_op (comb)
                    double comb = Compose(prodF, dIj);
                    Tn += Math.Ceiling(1.0 / n) * _tOp3;

                    // Финальная формула C[i][j]
                    double g = G[i][j];
                    double termA = Mult(Mult(prodF, Sub(Mult(3, g), 2)), g);
                    double termB = Mult(Sub(1, g), Add(dIj, Mult(Sub(Mult(4, comb), Mult(3, dIj)), g)));
                    Add(termA, termB);

                    Tn += Math.Ceiling(7.0 / n) * _tProd;
                    Tn += Math.Ceiling(3.0 / n) * _tNeg;
                    Tn += Math.Ceiling(2.0 / n) * _tSum;
                }
            }

            double T1 = _cntImp * _tImp + _cntProd * _tProd + _cntNeg * _tNeg + _cntSum * _tSum + _cntOp3 * _tOp3;
            double rVal = ComputeR(p, q, m);
            double tAvg = ComputeTavg(p, q, m);
            double lAvg = rVal > 0 ? tAvg / rVal : 1;
            Tn = Math.Max(Tn, 1e-9);

            double ky = T1 / Tn;
            double eff = ky / n;
            double d2 = lAvg > 0 ? Tn / lAvg : 0;

            return (ky, eff, d2, rVal);
        }


        #region Поиск параметров под ранг
        public (int p, int q, int m) FindParamsForR(int targetR, int maxVal = 15)
        {
            for (int p = 1; p <= maxVal; p++)
                for (int q = 1; q <= maxVal; q++)
                    for (int m = 1; m <= maxVal; m++)
                        if (ComputeR(p, q, m) == targetR)
                            return (p, q, m);
            return (0, 0, 0);
        }
        #endregion

        #region Построение графиков
        private void SavePlot(double[] x, double[] y1, double[] y2, string xl, string yl, string title, string l1, string l2, string fname, string dir)
        {
            var plot = new Plot();
            
            var s1 = plot.Add.Scatter(x, y1);
            s1.Label = l1;
            s1.LineWidth = 2;
            s1.MarkerSize = 5;

            var s2 = plot.Add.Scatter(x, y2);
            s2.Label = l2;
            s2.LineWidth = 2;
            s2.MarkerSize = 5;

            plot.XLabel(xl);
            plot.YLabel(yl);
            plot.Title(title);
            plot.ShowLegend();

            string path = Path.Combine(dir, fname);
            plot.SavePng(path, 1000, 600);
            Console.WriteLine($"  → Сохранено: {path}");
        }

        public void Build(string outputDir = "plots")
        {
            Directory.CreateDirectory(outputDir);
            Console.WriteLine("\n" + new string('=', 70));
            Console.WriteLine("ПОСТРОЕНИЕ ГРАФИКОВ");
            Console.WriteLine(new string('=', 70));

            // --- Графики зависимости от ранга (r) ---
            var rVals = new List<double>();
            var kyN8 = new List<double>(); var kyN10 = new List<double>();
            var effN8 = new List<double>(); var effN10 = new List<double>();
            var dN8 = new List<double>(); var dN10 = new List<double>();

            for (int size = 1; size <= 20; size++)
            {
                int p = size, q = size, m = size;
                rVals.Add(ComputeR(p, q, m));

                var (k4, e4, d4, _) = ComputeMetrics(p, q, m, n: 4);
                var (k8, e8, d8, _) = ComputeMetrics(p, q, m, n: 8);

                kyN8.Add(k4); kyN10.Add(k8);
                effN8.Add(e4); effN10.Add(e8);
                dN8.Add(d4); dN10.Add(d8);
            }

            SavePlot(rVals.ToArray(), kyN8.ToArray(), kyN10.ToArray(),
                "Ранг задачи (r)", "Коэффициент ускорения (Ky)",
                "Зависимость Ky от r", "n = 4", "n = 8", "Ky_vs_r.png", outputDir);

            SavePlot(rVals.ToArray(), effN8.ToArray(), effN10.ToArray(),
                "Ранг задачи (r)", "Эффективность (e)",
                "Зависимость e от r", "n = 4", "n = 8", "Eff_vs_r.png", outputDir);

            SavePlot(rVals.ToArray(), dN8.ToArray(), dN10.ToArray(),
                "Ранг задачи (r)", "Коэффициент расхождения (D)",
                "Зависимость D от r", "n = 4", "n = 8", "D_vs_r.png", outputDir);

            // --- Графики зависимости от количества ПЭ (n) ---
            var p32 = FindParamsForR(32);
            var p64 = FindParamsForR(64);

            if (p32.p != 0 && p64.p != 0)
            {
                int nMax = 51;
                var nVals = Enumerable.Range(1, nMax - 1).Select(x => (double)x).ToArray();
                var ky32 = new double[nMax - 1]; var ky48 = new double[nMax - 1];
                var eff32 = new double[nMax - 1]; var eff48 = new double[nMax - 1];
                var d32 = new double[nMax - 1]; var d48 = new double[nMax - 1];

                for (int n = 1; n < nMax; n++)
                {
                    var (k32, e32, d32v, _) = ComputeMetrics(p32.p, p32.q, p32.m, n);
                    var (k48, e48, d48v, _) = ComputeMetrics(p64.p, p64.q, p64.m, n);

                    ky32[n - 1] = k32; ky48[n - 1] = k48;
                    eff32[n - 1] = e32; eff48[n - 1] = e48;
                    d32[n - 1] = d32v; d48[n - 1] = d48v;
                }

                SavePlot(nVals, ky32, ky48,
                    "Процессорные элементы (n)", "Ky",
                    "Зависимость Ky от n", "r = 32", "r = 64", "Ky_vs_n.png", outputDir);

                SavePlot(nVals, eff32, eff48,
                    "Процессорные элементы (n)", "e",
                    "Зависимость e от n", "r = 32", "r = 64", "Eff_vs_n.png", outputDir);

                SavePlot(nVals, d32, d48,
                    "Процессорные элементы (n)", "D",
                    "Зависимость D от n", "r = 32", "r = 64", "D_vs_n.png", outputDir);
            }

            Console.WriteLine("\n✅ Все 6 графиков построены.");
        }
        #endregion
    }
}