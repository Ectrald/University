using Lab2_OKMD.Core;

namespace Lab2_OKMD;

public class InputManager
{
    private readonly string _filePath;
    
    public InputManager(string filePath)
    {
        _filePath = filePath;
    }
    
    public class InputData
    {
        public int P { get; set; }
        public int M { get; set; }
        public int Q { get; set; }
        public double[] OperationTimes { get; set; } = new double[5];
        public int Seed { get; set; } = 1;
    }
    
    public InputData ReadFromFile()
    {
        var lines = File.ReadAllLines(_filePath);
        if (lines.Length < 3)
            throw new Exception("Файл input.txt должен содержать минимум 3 строки");

        var data = new InputData();

        // Строка 1: p m q
        var dims = lines[0].Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (dims.Length != 3)
            throw new Exception("Первая строка должна содержать три числа: p m q");
        
        data.P = int.Parse(dims[0]);
        data.M = int.Parse(dims[1]);
        data.Q = int.Parse(dims[2]);
        
        if (data.P <= 0 || data.M <= 0 || data.Q <= 0)
            throw new Exception("Размерности должны быть положительными");

        // Строка 2: времена операций
        var times = lines[1].Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (times.Length != 5)
            throw new Exception("Вторая строка должна содержать 5 времён операций");
        
        for (int i = 0; i < 5; i++)
            data.OperationTimes[i] = double.Parse(times[i]);

        // Строка 3: seed (опционально)
        if (lines.Length > 2 && !string.IsNullOrWhiteSpace(lines[2]))
            data.Seed = int.Parse(lines[2].Trim());

        return data;
    }
}