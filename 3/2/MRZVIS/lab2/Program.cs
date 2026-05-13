using Lab2_OKMD;
using Lab2_OKMD.Core;
using Lab2_OKMD.Calculation;
using Lab2_OKMD.Metrics;
using Lab2_OKMD.Visualization;

namespace Lab2_OKMD;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("═".PadRight(70, '═'));
        Console.WriteLine("Лабораторная работа №2: ОКМД-архитектура — Вариант 7");
        Console.WriteLine("(~) = min,  /~\\ = *,  x~>y = 1+x*(y-1)");
        Console.WriteLine("═".PadRight(70, '═') + "\n");
        
        // 1. Чтение входных данных
        var inputMgr = new InputManager("input.txt");
        var input = inputMgr.ReadFromFile();
        
        Console.WriteLine($"📊 Параметры: p={input.P}, m={input.M}, q={input.Q}");
        Console.WriteLine($"⏱️  Времена операций: op3={input.OperationTimes[0]}, sum={input.OperationTimes[1]}, " +
                         $"imp={input.OperationTimes[2]}, prod={input.OperationTimes[3]}, neg={input.OperationTimes[4]}");
        Console.WriteLine($"🎲 Seed: {input.Seed}\n");
        
        // 2. Генерация матриц
        var rnd = new Random(input.Seed);
        var A = Operations.GenerateMatrix(input.P, input.M, rnd);
        var B = Operations.GenerateMatrix(input.M, input.Q, rnd);
        var E = Operations.GenerateVector(input.M, rnd);
        var G = Operations.GenerateMatrix(input.P, input.Q, rnd);
        
        // 3. Вычисление матрицы C
        // В main():
        var manual = new ManualCalculation(
            tImp: input.OperationTimes[0],
            tProd: input.OperationTimes[1], 
            tNeg: input.OperationTimes[2],
            tSum: input.OperationTimes[3],
            tOpС: input.OperationTimes[4]
        );

        manual.PrintMatrices();

        var c11 = manual.ComputeManualC00();
        manual.PrintResults(c11);
        
        // // 5. Построение графиков
        // Console.WriteLine("\n📈 Построение графиков...");
        // PlotBuilder.BuildPlots(20, input.OperationTimes, "plots");
        // PlotBuilder.BuildPlotsVsN(50, input.OperationTimes, "plots");
        //
        // Console.WriteLine("\n✅ Готово! Графики сохранены в папке 'plots/'");
        
        
        var builder = new GraphicsBuilder(
            tImp: 10, tProd: 5, tNeg: 3, tSum: 2, tOp3: 8
        );
        builder.Build("plots"); // Графики сохранятся в ./plots/
    }
}