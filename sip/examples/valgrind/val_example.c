  #include <stdlib.h>

  void f(void)
  {
     int* x = malloc(10 * sizeof(int));
     // problem 1: heap block overrun
     x[10] = 0;
     // problem 2: memory leak -- x not freed
  }

  int main(void)
  {
     f();
     return 0;
  }