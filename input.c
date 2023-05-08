#include<stdio.h>
#include<string.h>
int main() {
    int  b;
    scanf("%d",&a);
    scanf("%d",&b);
    int c = 0;
    if((b<0 && c<0 ) || (a>5)) {
        c=5;
        b=5;
    }

    printf("Result: %d", c);
    return 0;
}
