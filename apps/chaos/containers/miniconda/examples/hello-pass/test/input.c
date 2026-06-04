// Test input for HelloPass - contains various control flow patterns
#include <stdio.h>

int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

int fibonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;

    int a = 0, b = 1;
    int i = 2;
    while (i <= n) {
        int temp = a + b;
        a = b;
        b = temp;
        i++;
    }
    return b;
}

int classify(int x) {
    if (x > 100) {
        return 3;
    } else if (x > 50) {
        return 2;
    } else if (x > 0) {
        return 1;
    } else {
        return 0;
    }
}

int main() {
    printf("factorial(5) = %d\n", factorial(5));
    printf("fibonacci(10) = %d\n", fibonacci(10));
    printf("classify(75) = %d\n", classify(75));
    return 0;
}
