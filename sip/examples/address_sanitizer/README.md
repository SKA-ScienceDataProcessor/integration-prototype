
## Address Sanitizer Vs Valgrind

### Advantages are

- runs much faster and is able to catch a wider variety of bugs.
- much smaller CPU overheads 
- wider class of detected errors 
- full support of multi-threaded apps 

### Disadvantages are

- significant memory overhead which may be a limiting factor for resource limited 
environments ; it's still way better than Valgrind
- more complicated integration 
- MemorySanitizer is not reall easily usable at the moment as it requires one 
to rebuild all dependencies under Msan (including all standard libraries e.g. libstdc++); 
this means that casual users can only use Valgrind for detecting uninitialized errors
- sanitizers typically can not be combined with each other (the only supported 
combination is Asan+UBsan+Lsan) which means that you'll have to do separate QA 
runs to catch all types of bugs