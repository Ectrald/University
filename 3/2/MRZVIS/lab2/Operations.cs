using Lab2_OKMD.Core;

namespace Lab2_OKMD.Core;

public static class Operations
{
    /// <summary>
    /// Генерация случайной матрицы в диапазоне [-1, 1]
    /// </summary>
    public static double[,] GenerateMatrix(int rows, int cols, Random rnd)
    {
        var matrix = new double[rows, cols];
        for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
            matrix[i, j] = rnd.NextDouble() * (Constants.VALUE_MAX - Constants.VALUE_MIN) + Constants.VALUE_MIN;
        return matrix;
    }
    
    /// <summary>
    /// Генерация вектора-строки 1×m
    /// </summary>
    public static double[] GenerateVector(int length, Random rnd)
    {
        var vector = new double[length];
        for (int i = 0; i < length; i++)
            vector[i] = rnd.NextDouble() * (Constants.VALUE_MAX - Constants.VALUE_MIN) + Constants.VALUE_MIN;
        return vector;
    }
}