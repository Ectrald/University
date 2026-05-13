using System;
using System.Collections.Generic;
using System.Linq;

namespace Lab2_OKMD.Calculation;

/// <summary>
/// Ручной расчёт C[0,0] с разбиением на слои (ЯПФ) + вычисление полной матрицы C.
/// Вариант: (~) = /1\ = min, /~\ = /2\ = *, x~>y = 1+x*(y-1)
/// </summary>
public class ManualCalculation
{
    // Времена операций (из input.txt)
    public double TImp { get; }      // время импликации
    public double TProd { get; }     // время умножения
    public double TNeg { get; }      // время вычитания
    public double TSum { get; }      // время сложения
    public double TOpС { get; }      // время (~) = min

    // Результаты расчёта метрик
    public double LSum { get; private set; }
    public double LAvg { get; private set; }
    
    // Фиксированный ранг для p=m=q=2 (как в Python-примере)
    private const int RFinal = 94;
    
    // Исходные матрицы
    private readonly double[,] A, B, G;
    private readonly double[] E;
    
    public ManualCalculation(double tImp, double tProd, double tNeg, double tSum, double tOpС)
    {
        TImp = tImp; TProd = tProd; TNeg = tNeg; TSum = tSum; TOpС = tOpС;
        
        // Фиксированный seed для воспроизводимости
        var rnd = new Random(1);
        const int p = 2, m = 2, q = 2;
        
        A = GenerateMatrix(p, m, rnd);
        B = GenerateMatrix(m, q, rnd);
        E = GenerateVector(m, rnd);
        G = GenerateMatrix(p, q, rnd);
    }
    
    // ─────────────────────────────────────────────────────────────
    // Базовые операции (ВАШ ВАРИАНТ)
    // ─────────────────────────────────────────────────────────────
    
    /// <summary>
    /// Импликация: x~>y = 1 + x·(y-1)
    /// </summary>
    private static double Imp(double x, double y) => 1.0 + x * (y - 1.0);
    
    /// <summary>
    /// Композиция (~) = /1\ = min(x, y)
    /// </summary>
    private static double Compose(double x, double y) => Math.Min(x, y);
    
    /// <summary>
    /// Редукция /~\ = /2\ = произведение: Π x[k]
    /// </summary>
    private static double ReduceProd(IEnumerable<double> values) => 
        values.Aggregate(1.0, (acc, v) => acc * v);
    
    /// <summary>
    /// Объединение \~/k = 1 - Π(1 - x[k])
    /// </summary>
    private static double ReduceUnion(IEnumerable<double> values) => 
        1.0 - values.Aggregate(1.0, (acc, v) => acc * (1.0 - v));
    
    // ─────────────────────────────────────────────────────────────
    // Генерация матриц
    // ─────────────────────────────────────────────────────────────
    
    private static double[,] GenerateMatrix(int rows, int cols, Random rnd)
    {
        var m = new double[rows, cols];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                m[i, j] = rnd.NextDouble() * 2.0 - 1.0; // [-1, 1]
        return m;
    }
    
    private static double[] GenerateVector(int length, Random rnd)
    {
        var v = new double[length];
        for (int i = 0; i < length; i++)
            v[i] = rnd.NextDouble() * 2.0 - 1.0;
        return v;
    }
    
    public void PrintMatrices()
    {
        Console.WriteLine("Исходные матрицы:");
        Console.WriteLine($"A =\n{FormatMatrix(A)}");
        Console.WriteLine($"B =\n{FormatMatrix(B)}");
        Console.WriteLine($"E =\n{FormatVector(E)}");
        Console.WriteLine($"G =\n{FormatMatrix(G)}");
    }
    
    private static string FormatMatrix(double[,] m)
    {
        var rows = m.GetLength(0);
        var cols = m.GetLength(1);
        var lines = new List<string>();
        for (int i = 0; i < rows; i++)
        {
            var line = "  [ ";
            for (int j = 0; j < cols; j++)
                line += $"{m[i, j],10:F6} ";
            line += "]";
            lines.Add(line);
        }
        return string.Join("\n", lines);
    }
    
    private static string FormatVector(double[] v)
    {
        var line = "  [ ";
        foreach (var val in v) line += $"{val,10:F6} ";
        line += "]";
        return line;
    }
    
    // ─────────────────────────────────────────────────────────────
    // Ручной расчёт C[0,0] с разбиением на слои (ЯПФ)
    // ─────────────────────────────────────────────────────────────
    
    /// <summary>
    /// Ручной расчёт C[0,0] с явным разбиением на слои.
    /// Каждый слой — независимые операции, выполняемые параллельно в ОКМД.
    /// Вариант: (~)=min, /~\=*, x~>y=1+x*(y-1)
    /// </summary>
    public double ComputeManualC00()
    {
        LSum = 0; LAvg = 0;
        var a = A; var b = B; var e = E; var g = G;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 1 (ранг 2): Импликации, d-компоненты, предвычисления
        // ═══════════════════════════════════════════════════════
        // Операции:
        // • 4 импликации: imp(A[0,0],B[0,0]), imp(B[0,0],A[0,0]), imp(A[0,1],B[1,0]), imp(B[1,0],A[0,1])
        // • 2 умножения для d: d1=A[0,0]*B[0,0], d2=A[0,1]*B[1,0]  [/~\ = *]
        // • 3 умножения на константы: E[0]*2, E[1]*2, G[0,0]*3
        // • 3 вычитания: 1-E[0], 1-E[1], 1-G[0,0]
        var impl_ab  = Imp(a[0, 0], b[0, 0]);  // ранг 2
        var impl_ba  = Imp(b[0, 0], a[0, 0]);  // ранг 2
        var impl_ab_ = Imp(a[0, 1], b[1, 0]);  // ранг 2
        var impl_ba_ = Imp(b[1, 0], a[0, 1]);  // ранг 2
        
        var d1 = a[0, 0] * b[0, 0];  // /~\ = *, ранг 2
        var d2 = a[0, 1] * b[1, 0];  // ранг 2
        
        var e2_0 = e[0] * 2;  // ранг 2
        var e2_1 = e[1] * 2;  // ранг 2
        var g3   = g[0, 0] * 3;  // ранг 2
        
        var e11 = 1 - e[0];  // ранг 2
        var e12 = 1 - e[1];  // ранг 2
        var g1  = 1 - g[0, 0];  // ранг 2
        
        LSum += 4 * TImp + 2 * TProd + 3 * TProd + 3 * TNeg;
        LAvg += (4 * 2 * TImp + 2 * 2 * TProd + 3 * 2 * TProd + 3 * 2 * TNeg) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 2 (ранг 3): Умножения на константы, вычитания
        // ═══════════════════════════════════════════════════════
        var impl_4   = impl_ab * 4;      // ранг 3
        var impl_4_  = impl_ab_ * 4;     // ранг 3
        var e11_2_1  = e2_0 - 1;         // ранг 3
        var e12_2_1  = e2_1 - 1;         // ранг 3
        var d1_1     = 1 - d1;           // ранг 3
        var d2_1     = 1 - d2;           // ранг 3
        var g_32     = g3 - 2;           // ранг 3
        
        LSum += 2 * TProd + 5 * TNeg;
        LAvg += (2 * 3 * TProd + 5 * 3 * TNeg) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 3 (ранги 4-6): Предвычисления для term1/term2, Pk
        // ═══════════════════════════════════════════════════════
        var impl_4_2   = impl_4 - 2;         // ранг 4
        var impl_4_2_  = impl_4_ - 2;        // ранг 4
        var ab_e11     = e11_2_1 * impl_ab;  // ранг 5
        var ab_e11_    = e12_2_1 * impl_ab_; // ранг 5
        var pk         = d1_1 * d2_1;        // ранг 6
        var gg_32      = g_32 * g[0, 0];     // ранг 4
        
        LSum += 2 * TNeg + 4 * TProd;
        LAvg += (2 * 4 * TNeg + (2 * 5 + 1 * 6 + 1 * 4) * TProd) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 4 (ранги 5,7): temp1/2, d11
        // ═══════════════════════════════════════════════════════
        var temp1 = e[0] * impl_4_2;   // ранг 5
        var temp2 = e[1] * impl_4_2_;  // ранг 5
        var d11   = 1 - pk;            // ранг 7
        
        LSum += 2 * TProd + TNeg;
        LAvg += (2 * 5 * TProd + 1 * 7 * TNeg) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 5 (ранги 6,8): temp+1, part1, d11*3
        // ═══════════════════════════════════════════════════════
        var temp1_1 = temp1 + 1;           // ранг 6
        var temp2_1 = temp2 + 1;           // ранг 6
        var part1_1 = ab_e11 * e[0];       // ранг 6
        var part1_2 = ab_e11_ * e[1];      // ранг 6
        var d11_3   = d11 * 3;             // ранг 8
        
        LSum += 2 * TSum + 3 * TProd;
        LAvg += (2 * 6 * TSum + (2 * 6 + 1 * 8) * TProd) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 6 (ранг 8): temp = impl_ba * temp1_1
        // ═══════════════════════════════════════════════════════
        var temp  = impl_ba * temp1_1;  // ранг 8
        var temp_ = impl_ba_ * temp2_1; // ранг 8
        
        LSum += 2 * TProd;
        LAvg += (2 * 8 * TProd) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 7 (ранг 10): part2 = temp * E11
        // ═══════════════════════════════════════════════════════
        var part2_1 = temp * e11;   // ранг 10
        var part2_2 = temp_ * e12;  // ранг 10
        
        LSum += 2 * TProd;
        LAvg += (2 * 10 * TProd) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 8 (ранги 3,16): f111/f112, d1_1/d2_1
        // ═══════════════════════════════════════════════════════
        var f111 = part2_1 + part1_1;  // ранг 16
        var f112 = part2_2 + part1_2;  // ранг 16
        
        LSum += 2 * TSum;
        LAvg += (2 * 16 * TSum) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 9 (ранг 32): f_prod = f111 * f112
        // ═══════════════════════════════════════════════════════
        var f_prod = f111 * f112;  // ранг 32
        
        LSum += TProd;
        LAvg += (TProd * 32) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 10 (ранги 36,39): df = Compose(d11, f_prod), part_c_1
        // ═══════════════════════════════════════════════════════
        var df = Compose(d11, f_prod);  // (~) = min, ранг 39
        var part_c_1 = gg_32 * f_prod;  // ранг 36
        
        LSum += TOpС + TProd;
        LAvg += (39 * TOpС + 36 * TProd) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 11 (ранг 40): df4 = df * 4
        // ═══════════════════════════════════════════════════════
        var df4 = df * 4;  // ранг 40
        
        LSum += TProd;
        LAvg += (40 * TProd) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 12 (ранг 48): dd4 = df4 - d11_3
        // ═══════════════════════════════════════════════════════
        var dd4 = df4 - d11_3;  // ранг 48
        
        LSum += TNeg;
        LAvg += (48 * TNeg) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 13 (ранг 49): dd4g = dd4 * G[0,0]
        // ═══════════════════════════════════════════════════════
        var dd4g = dd4 * g[0, 0];  // ранг 49
        
        LSum += TProd;
        LAvg += (49 * TProd) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 14 (ранг 56): ddd4g = dd4g + d11
        // ═══════════════════════════════════════════════════════
        var ddd4g = dd4g + d11;  // ранг 56
        
        LSum += TSum;
        LAvg += (56 * TSum) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 15 (ранг 58): part_c_2 = ddd4g * G1
        // ═══════════════════════════════════════════════════════
        var part_c_2 = ddd4g * g1;  // ранг 58
        
        LSum += TProd;
        LAvg += (TProd * 58) / RFinal;
        
        // ═══════════════════════════════════════════════════════
        // СЛОЙ 16 (ранг 94): C_11 = part_c_2 + part_c_1
        // ═══════════════════════════════════════════════════════
        var c11 = part_c_2 + part_c_1;  // ранг 94
        
        LSum += TSum;
        LAvg += (TSum * 94) / RFinal;
        
        return c11;
    }
    
    // ─────────────────────────────────────────────────────────────
    // Вычисление полной матрицы C (автоматическое, без слоёв)
    // ─────────────────────────────────────────────────────────────
    
    /// <summary>
    /// Вычисление полной матрицы C по общей формуле.
    /// Используется для верификации ручного расчёта C[0,0].
    /// Вариант: (~)=min, /~\=*, x~>y=1+x*(y-1)
    /// </summary>
    public double[,] ComputeFullC()
    {
        var p = A.GetLength(0);
        var q = B.GetLength(1);
        var m = A.GetLength(1);
        var C = new double[p, q];
        
        for (int i = 0; i < p; i++)
        {
            for (int j = 0; j < q; j++)
            {
                var fList = new List<double>();
                var dList = new List<double>();
                
                for (int k = 0; k < m; k++)
                {
                    var a = A[i, k];
                    var b = B[k, j];
                    var e = E[k];
                    
                    // d_temp = a /~\ b = a * b  [/~\ = /2\ = *]
                    var dTemp = a * b;
                    dList.Add(dTemp);
                    
                    // Импликации: x~>y = 1 + x*(y-1)
                    var impAB = Imp(a, b);
                    var impBA = Imp(b, a);
                    
                    // f(i,j,k) = impAB*(2e-1)*e + impBA*(1+(4*impAB-2)*e)*(1-e)
                    var term1 = impAB * (2 * e - 1) * e;
                    var term2 = impBA * (1 + (4 * impAB - 2) * e) * (1 - e);
                    fList.Add(term1 + term2);
                }
                
                // Редукции
                var F = ReduceProd(fList);           // /~\k f = Πk f  [/~\ = /2\ = *]
                var D = ReduceUnion(dList);          // \~/k d = 1 - Πk(1-d)
                
                // Комбинация: comb = F (~) D = min(F, D)  [(~) = /1\ = min]
                var comb = Compose(F, D);
                
                // Финальная формула:
                // C[i][j] = F*(3g-2)*g + (1-g)*(D + (4*comb - 3*D)*g)
                var g = G[i, j];
                var termA = F * (3 * g - 2) * g;
                var termB = (1 - g) * (D + (4 * comb - 3 * D) * g);
                C[i, j] = termA + termB;
            }
        }
        return C;
    }
    
    // ─────────────────────────────────────────────────────────────
    // Вывод результатов
    // ─────────────────────────────────────────────────────────────
    
    public void PrintResults(double c11Manual)
    {
        Console.WriteLine("Результат:");
        var C = ComputeFullC();
        Console.WriteLine("Матрица C:");
        Console.WriteLine(FormatMatrix(C));
        Console.WriteLine($"\nC_11 = {c11Manual}");
        Console.WriteLine($"L_sum = {LSum}");
        Console.WriteLine($"L_avg = {LAvg}");
        Console.WriteLine($"D = {(LAvg > 0 ? LSum / LAvg : 0):F3}");
        

        // Console.WriteLine("\nРезультирующая матрица C:");

        
        // Верификация
        var c11Full = C[0, 0];
        var diff = Math.Abs(c11Manual - c11Full);
        Console.WriteLine($"\nВерификация: C[0,0] из ComputeFullC = {c11Full}");
        Console.WriteLine($"Разница: {diff:E2} {(diff < 1e-10 ? "✓ OK" : "✗ МНОГО")}");
    }
}