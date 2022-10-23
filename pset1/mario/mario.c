#include <stdio.h>
#include <cs50.h>

int main(void)
{
    int height;
    do
    {
        height = get_int("What will be the height of the pyramid? (1-8) \n");
    }
    while (height > 8 || height < 1);

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < height; j++)
        {
            if (i + j < height - 1)
            {
                printf(" ");
            }
            else
            {
                printf("#");
            }
        }
        printf("\n");
    }
}
