#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // TODO: Prompt for start size
    int start;
    {
        do
        {
            start = get_int("How many llamas are there in the start? \n");
        }
        while (start < 9);
    }
    // TODO: Prompt for end size
    int end;
    {
        do
        {
            end = get_int("How many llamas should there be in the end? \n");
        }
        while (end < start);
    }
    // TODO: Calculate number of years until we reach threshold
    int pop = start;
    int years = 0;
    while (pop < end)
    {
        int decline = pop / 4;
        int growth = pop / 3;
        pop = pop + growth - decline;
        years++;
    }
    // TODO: Print number of years
    printf("Years: %i\n", years);
}