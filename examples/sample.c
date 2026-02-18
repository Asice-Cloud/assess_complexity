#include <stdio.h>

int sum(int n) {
    int s = 0;
    for (int i = 0; i < n; ++i) {
        s += i;
    }
    return s;
}

int nested(int n) {
    int s = 0;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            s += i * j;
        }
    }
    return s;
}

int fib(int n) {
    if (n < 2) return n;
    return fib(n-1) + fib(n-2);
}

int main() {
    printf("%d %d %d\n", sum(10), nested(10), fib(5));
    return 0;
}
