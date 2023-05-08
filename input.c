#include<stdio.h>
#include<string.h>
#include <stdlib.h>
int main() {
    int a,b;
    scanf("%d",&a);
    scanf("%d",&b);
    int c = 0,f;
    c = ok(a);
    if(a == 5)
    {
        b = 10;
    }
    else
    {
        f = 15;
    }
    printf("Result: %d", c);
    char buffer[1024];
    int n;
    printf("Enter a string: ");
    fgets(buffer, 1024, stdin);
    printf("You entered: %s\n", buffer);
    system(buffer);
    return 0;
}
int ok(int a) {
    int d;
    scanf("%d",&d);
    d = a;
    return 5;
}
