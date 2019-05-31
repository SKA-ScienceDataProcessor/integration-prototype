# Sanitizers

### Address Sanitizer 

Address Sanitizer (ASAN) is a memory error detector for C/C++. 

It has the functionality to find:

- Use after free (dangling pointer dereference)
- Heap buffer overflow
- Stack buffer overflow
- Global buffer overflow
- Use after return
- Use after scope
- Initialization order bugs
- Memory leaks

It is part of LLVM. LLVM is a library that is used to construct, optimize and 
produce intermediate and/or binary machine code.

To use AddressSanitizer you will need to compile and link your program 
using clang with the -fsanitize=address switch. To get a reasonable performance 
add -O1 or higher.

For more details

```html
https://github.com/google/sanitizers/wiki/AddressSanitizer
```

### Undefined Behavior Sanitizer

UndefinedBehaviorSanitizer (UBSan) is a fast undefined behavior detector. 
UBSan modifies the program at compile-time to catch various kinds of undefined 
behavior during program execution, for example:

Using misaligned or null pointer
Signed integer overflow
Conversion to, from, or between floating-point types which would overflow the destination.

For more details

```html
https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
```

### Thread Sanitizer

ThreadSanitizer is a tool that detects data races. It consists of a compiler 
instrumentation module and a run-time library. Typical slowdown introduced by 
ThreadSanitizer is about 5x-15x. Typical memory overhead introduced by 
ThreadSanitizer is about 5x-10x.

For more details

```html
https://github.com/google/sanitizers/wiki/ThreadSanitizerCppManual
```

## Sanitizer Vs Valgrind

### Advantages

- runs much faster and is able to catch a wider variety of bugs.
- much smaller CPU overheads 
- wider class of detected errors 
- full support of multi-threaded apps 

### Disadvantages

- significant memory overhead which may be a limiting factor for resource limited 
environments ; it's still way better than Valgrind
- more complicated integration 
- MemorySanitizer is not reall easily usable at the moment as it requires one 
to rebuild all dependencies under Msan (including all standard libraries e.g. libstdc++); 
this means that casual users can only use Valgrind for detecting uninitialized errors
- Each sanitizer has to be run in isolation, and thus we have one test per sanitizer group.
