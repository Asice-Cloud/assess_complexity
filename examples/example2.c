#include <stdio.h>
#include <stdlib.h>

#define MAX_N 10
int n; 
int dist[MAX_N][MAX_N]; 
int dp[1 << MAX_N][MAX_N]; 

int tsp(int mask, int pos) {
    if (mask == (1 << n) - 1) { 
        return dist[pos][0]; 
    }
    if (dp[mask][pos] != -1) { 
        return dp[mask][pos];
    }
    int ans = 1e9; 
    for (int city = 0; city < n; city++) {
        if ((mask & (1 << city)) == 0) {
            int newAns = dist[pos][city] + tsp(mask | (1 << city), city);
            ans = ans < newAns ? ans : newAns; 
        }
    }
    return dp[mask][pos] = ans; 
}

int main() {
    n = 3; 
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i == j) {
                dist[i][j] = 0;
            } else {
                dist[i][j] = rand() % 10 + 1; 
            }
        }
    }
    for (int i = 0; i < (1 << n); i++) {
        for (int j = 0; j < n; j++) {
            dp[i][j] = -1; 
        }
    }

    int result = tsp(1, 0); 
    printf("min length: %d\n", result);
    return 0;
} 