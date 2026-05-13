using ScottPlot;
using ScottPlot.Plottables;
using Lab2_OKMD.Metrics;

namespace Lab2_OKMD.Visualization;

public static class PlotBuilder
{

    // Вспомогательный метод для настройки легенды
    private static void ConfigureLegend(Plot plt, Alignment location)
    {
        plt.Legend.IsVisible = true;
        plt.Legend.Location = location;
    }

    public static void BuildPlots(int maxR, double[] opTimes, string outputDir)
    {
        Directory.CreateDirectory(outputDir);
        
        var (ranks, speedup, efficiency) = MetricsCalculator.Calculate(8, 10, maxR, opTimes);
        
        // График 1: Зависимость коэффициента ускорения от ранга
        var plt1 = new Plot();
        plt1.Title("Зависимость коэффициента ускорения от ранга задачи");
        plt1.XLabel("Ранг задачи (r)");
        plt1.YLabel("Коэффициент ускорения (Ky)");
        
        var scatter1 = plt1.Add.Scatter(ranks, speedup);
        scatter1.Label = "n = 8, 10 (среднее)";
        scatter1.LineWidth = 2;
        scatter1.MarkerSize = 6;
        
        ConfigureLegend(plt1, Alignment.UpperRight);
        
        plt1.SavePng($"{outputDir}/ky_vs_r.png", 900, 600);
        
        // График 2: Зависимость эффективности от ранга
        var plt2 = new Plot();
        plt2.Title("Зависимость эффективности от ранга задачи");
        plt2.XLabel("Ранг задачи (r)");
        plt2.YLabel("Эффективность (Eff)");
        
        var scatter2 = plt2.Add.Scatter(ranks, efficiency);
        scatter2.Label = "n = 8, 10 (среднее)";
        scatter2.LineWidth = 2;
        scatter2.MarkerSize = 6;
        
        ConfigureLegend(plt2, Alignment.UpperRight);
        
        plt2.SavePng($"{outputDir}/eff_vs_r.png", 900, 600);
        
        Console.WriteLine($"✓ Сохранено: {outputDir}/ky_vs_r.png, eff_vs_r.png");
    }
    
    public static void BuildPlotsVsN(int maxN, double[] opTimes, string outputDir)
    {
        Directory.CreateDirectory(outputDir);
        
        var pltKy = new Plot();
        pltKy.Title("Зависимость коэффициента ускорения от количества ПЭ");
        pltKy.XLabel("Количество процессорных элементов (n)");
        pltKy.YLabel("Коэффициент ускорения (Ky)");
        
        var pltEff = new Plot();
        pltEff.Title("Зависимость эффективности от количества ПЭ");
        pltEff.XLabel("Количество процессорных элементов (n)");
        pltEff.YLabel("Эффективность (Eff)");
        
        int[] targetRs = { 32, 48, 64 };
        var colors = new[] { Colors.Blue, Colors.Red, Colors.Green };
        
        for (int idx = 0; idx < targetRs.Length; idx++)
        {
            int r = targetRs[idx];
            var (nVals, speedup, efficiency) = MetricsCalculator.CalculateVsN(r, maxN, opTimes);
            
            var scatKy = pltKy.Add.Scatter(nVals, speedup);
            scatKy.Label = $"r = {r}";
            scatKy.Color = colors[idx];
            scatKy.LineWidth = 2;
            scatKy.MarkerSize = 5;
            
            var scatEff = pltEff.Add.Scatter(nVals, efficiency);
            scatEff.Label = $"r = {r}";
            scatEff.Color = colors[idx];
            scatEff.LineWidth = 2;
            scatEff.MarkerSize = 5;
        }
        
        ConfigureLegend(pltKy, Alignment.MiddleRight);
        
        ConfigureLegend(pltEff, Alignment.MiddleRight);
        
        pltKy.SavePng($"{outputDir}/ky_vs_n.png", 950, 650);
        pltEff.SavePng($"{outputDir}/eff_vs_n.png", 950, 650);
        
        Console.WriteLine($"✓ Сохранено: {outputDir}/ky_vs_n.png, eff_vs_n.png");
    }
}