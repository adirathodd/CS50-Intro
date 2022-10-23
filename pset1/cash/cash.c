#include <cs50.h>
#include <stdio.h>
#include <math.h>

int main(void)
{
    float cents;
    do
    {
        cents = get_float("Change Owed: ");
    }
    while (cents < 0.00);
    int change = round(cents * 100);

    int q = 0;
    int d = 0;
    int n = 0;
    int p = 0;
    while (change > 0)
    {
        if (change >= 25)
        {
            q++;
            change -= 25;
        }
        else if (change >= 10)
        {
            d++;
            change -= 10;
        }
        else if (change >= 5)
        {
            n++;
            change -= 5;
        }
        else
        {
            p++;
            change -= 1;
        }
    }
    printf("Quarters: %i\n", q);
    printf("Dimes: %i\n", d);
    printf("Nickels: %i\n", n);
    printf("Pennies: %i\n", p);
}