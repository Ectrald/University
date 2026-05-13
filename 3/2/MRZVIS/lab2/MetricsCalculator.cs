using Lab2_OKMD.Core;
using Lab2_OKMD.Calculation;

namespace Lab2_OKMD.Metrics;

public static class MetricsCalculator
{
    /// <summary>
    /// Расчёт метрик для разных рангов задачи (при фиксированных n)
    /// </summary>
    public static (double[] ranks, double[] speedup, double[] efficiency) 
        Calculate(int n1, int n2, int maxR, double[] opTimes)
    {
        var ranks = new List<double>();
        var ky1 = new List<double>();
        var ky2 = new List<double>();
        var eff1 = new List<double>();
        var eff2 = new List<double>();
        
        for (int size = 1; size <= maxR; size++)
        {
            int p = size, m = size, q = size;
            double r = ComputeRank(p, q, m);
            ranks.Add(r);
            
            var (k1, e1) = ComputeMetrics(p, q, m, n1, opTimes);
            var (k2, e2) = ComputeMetrics(p, q, m, n2, opTimes);
            
            ky1.Add(k1); ky2.Add(k2);
            eff1.Add(e1); eff2.Add(e2);
        }
        
        // Возвращаем средние значения для двух n
        var speedup = ky1.Zip(ky2, (a, b) => (a + b) / 2).ToArray();
        var efficiency = eff1.Zip(eff2, (a, b) => (a + b) / 2).ToArray();
        
        return (ranks.ToArray(), speedup, efficiency);
    }
    
    /// <summary>
    /// Расчёт метрик для разных n (при фиксированных r)
    /// </summary>
    public static (double[] nVals, double[] speedup, double[] efficiency) 
        CalculateVsN(int targetR, int maxN, double[] opTimes)
    {
        var nVals = Enumerable.Range(1, maxN).Select(x => (double)x).ToArray();
        var speedup = new double[maxN];
        var efficiency = new double[maxN];
        
        // Находим p,q,m дающие нужный ранг
        var (p, q, m) = FindParamsForRank(targetR);
        if (p == 0) return (nVals, speedup, efficiency);
        
        for (int i = 0; i < maxN; i++)
        {
            int n = i + 1;
            var (ky, eff) = ComputeMetrics(p, q, m, n, opTimes);
            speedup[i] = ky;
            efficiency[i] = eff;
        }
        
        return (nVals, speedup, efficiency);
    }
    
    /// <summary>
    /// Вычисление ранга задачи: r = p*q + q*m + p*m + m + p*q
    /// </summary>
    private static double ComputeRank(int p, int q, int m)
    {
        return p * q + q * m + p * m + m + p * q;
    }
    
    /// <summary>
    /// Поиск размерностей для заданного ранга
    /// </summary>
    private static (int, int, int) FindParamsForRank(int targetR, int maxVal = 15)
    {
        for (int p = 1; p <= maxVal; p++)
            for (int q = 1; q <= maxVal; q++)
                for (int m = 1; m <= maxVal; m++)
                    if (ComputeRank(p, q, m) == targetR)
                        return (p, q, m);
        return (0, 0, 0);
    }
    
    /// <summary>
    /// Расчёт коэффициента ускорения и эффективности
    /// </summary>
    private static (double Ky, double Eff) ComputeMetrics(int p, int q, int m, int n, double[] opTimes)
    {
        // Последовательное время (упрощённая оценка)
        double opsPerElement = m * (2 * opTimes[Constants.IDX_IMP] + 8 * opTimes[Constants.IDX_PROD] + 
                                    3 * opTimes[Constants.IDX_NEG] + 2 * opTimes[Constants.IDX_SUM]) +
                               (2 * m - 1) * opTimes[Constants.IDX_PROD] + (m + 1) * opTimes[Constants.IDX_NEG] +
                               opTimes[Constants.IDX_OP3] + 7 * opTimes[Constants.IDX_PROD] + 
                               3 * opTimes[Constants.IDX_NEG] + 2 * opTimes[Constants.IDX_SUM];
        
        double T1 = p * q * opsPerElement;
        
        // Параллельное время: Tn = Σ ceil(ops/n) * t_op
        double Tn = 0;
        // Грубая оценка: делим общее количество операций на n
        Tn = T1 / n + Math.Ceiling(Math.Log2(Math.Max(m, 2))) * opTimes[Constants.IDX_PROD];
        
        double Ky = T1 / Math.Max(Tn, 1e-9);
        double Eff = Ky / n;
        
        // Ограничиваем эффективность единицей
        Eff = Math.Min(Eff, 1.0);
        
        return (Ky, Eff);
    }
}