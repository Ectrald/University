namespace Lab2_OKMD.Core;

public static class Constants
{
    // Вариант: (~) = /1\ = min, /~\ = /2\ = *, x~>y = 1+x*(y-1)
    
    public const double VALUE_MIN = -1.0;
    public const double VALUE_MAX = 1.0;
    
    // Индексы времён операций в массиве
    public const int IDX_OP3 = 0;   // (~) и /~\
    public const int IDX_SUM = 1;   // сложение
    public const int IDX_IMP = 2;   // импликация
    public const int IDX_PROD = 3;  // умножение
    public const int IDX_NEG = 4;   // вычитание/отрицание
}