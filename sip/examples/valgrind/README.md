# Valgrind

Valgrind is an instrumentation framework for building dynamic analysis tools. 

The Valgrind distribution currently includes six production-quality tools: a 
memory error detector, two thread error detectors, a cache and branch-prediction 
profiler, a call-graph generating cache and branch-prediction profiler, and a 
heap profiler. It also includes three experimental tools: a stack/global array 
overrun detector, a second heap profiler that examines how heap blocks are used, 
and a SimPoint basic block vector generator.

The most popular of these tools is called Memcheck. It can detect many memory-related 
errors that are common in C and C++ programs and that can lead to crashes and 
unpredictable behaviour.

A number of useful tools are supplied as standard.


- Memcheck is a memory error detector. It helps you make your programs, particularly 
those written in C and C++, more correct.

- Cachegrind is a cache and branch-prediction profiler. It helps you make your 
programs run faster.

- Callgrind is a call-graph generating cache profiler. It has some overlap with 
Cachegrind, but also gathers some information that Cachegrind does not.

- Helgrind is a thread error detector. It helps you make your multi-threaded 
programs more correct.

- DRD is also a thread error detector. It is similar to Helgrind but uses 
different analysis techniques and so may find different problems.

- Massif is a heap profiler. It helps you make your programs use less memory.

- DHAT is a different kind of heap profiler. It helps you understand issues of 
block lifetimes, block utilisation, and layout inefficiencies.

- SGcheck is an experimental tool that can detect overruns of stack and global 
arrays. Its functionality is complementary to that of Memcheck: SGcheck finds 
problems that Memcheck can't, and vice versa..

- BBV is an experimental SimPoint basic block vector generator. It is useful to 
people doing computer architecture research and development.

## Install Valgrind

```bash
sudo apt install valgrind
```

## Running program under Memcheck

```bash
valgrind --leak-check=yes ./myprog
```

Most error messages look like the following, which describes problem 1, 
the heap block overrun:

```text
  ==19182== Invalid write of size 4
  ==19182==    at 0x804838F: f (example.c:6)
  ==19182==    by 0x80483AB: main (example.c:11)
  ==19182==  Address 0x1BA45050 is 0 bytes after a block of size 40 alloc'd
  ==19182==    at 0x1B8FF5CD: malloc (vg_replace_malloc.c:130)
  ==19182==    by 0x8048385: f (example.c:5)
  ==19182==    by 0x80483AB: main (example.c:11)
```

Things to notice:

The 19182 is the process ID; it's usually unimportant.

The first line ("Invalid write...") tells you what kind of error it is. Here, 
the program wrote to some memory it should not have due to a heap block overrun.

Below the first line is a stack trace telling you where the problem occurred. 
Stack traces can get quite large, and be confusing, especially if you are using 
the C++ STL. Reading them from the bottom up can help. If the stack trace is not 
big enough, use the --num-callers option to make it bigger.

The code addresses (eg. 0x804838F) are usually unimportant, but occasionally 
crucial for tracking down weirder bugs.

Some error messages have a second component which describes the memory address 
involved. This one shows that the written memory is just past the end of a 
block allocated with malloc() on line 5 of example.c.

It's worth fixing errors in the order they are reported, as later errors can be 
caused by earlier errors. Failing to do this is a common cause of difficulty with Memcheck.

Memory leak messages look like this

```text
  ==19182== 40 bytes in 1 blocks are definitely lost in loss record 1 of 1
  ==19182==    at 0x1B8FF5CD: malloc (vg_replace_malloc.c:130)
  ==19182==    by 0x8048385: f (a.c:5)
  ==19182==    by 0x80483AB: main (a.c:11)
```

The stack trace tells you where the leaked memory was allocated. Memcheck cannot 
tell you why the memory leaked, unfortunately. (Ignore the "vg_replace_malloc.c", 
that's an implementation detail.)

There are several kinds of leaks; the two most important categories are:

"definitely lost": your program is leaking memory -- fix it!

"probably lost": your program is leaking memory, unless you're doing funny things 
with pointers (such as moving them to point to the middle of a heap block).

Memcheck also reports uses of uninitialised values, most commonly with the message 
"Conditional jump or move depends on uninitialised value(s)". It can be difficult 
to determine the root cause of these errors. Try using the --track-origins=yes to 
get extra information. This makes Memcheck run slower, but the extra information 
you get often saves a lot of time figuring out where the uninitialised values are 
coming from.

Memcheck is not perfect; it occasionally produces false positives, and there are 
mechanisms for suppressing these (see Suppressing errors in the Valgrind User Manual). 
However, it is typically right 99% of the time, so you should be wary of ignoring its 
error messages. After all, you wouldn't ignore warning messages produced by a compiler, 
right? The suppression mechanism is also useful if Memcheck is reporting errors in 
library code that you cannot change. The default suppression set hides a lot of these, 
but you may come across more.

## Example

To run the example, run the following commands:

```bash
gcc -o myprog val_example.c
valgrind --leak-check=yes ./myprog 
```

This produces an output as follows:

```text
==26339== Memcheck, a memory error detector
==26339== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==26339== Using Valgrind-3.13.0 and LibVEX; rerun with -h for copyright info
==26339== Command: ./myprog
==26339== 
==26339== Invalid write of size 4
==26339==    at 0x108668: f (in /home/njthykkathu/SKA/UKSW-29/integration-prototype/sip/examples/valgrind/myprog)
==26339==    by 0x108679: main (in /home/njthykkathu/SKA/UKSW-29/integration-prototype/sip/examples/valgrind/myprog)
==26339==  Address 0x522d068 is 0 bytes after a block of size 40 alloc'd
==26339==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==26339==    by 0x10865B: f (in /home/njthykkathu/SKA/UKSW-29/integration-prototype/sip/examples/valgrind/myprog)
==26339==    by 0x108679: main (in /home/njthykkathu/SKA/UKSW-29/integration-prototype/sip/examples/valgrind/myprog)
==26339== 
==26339== 
==26339== HEAP SUMMARY:
==26339==     in use at exit: 40 bytes in 1 blocks
==26339==   total heap usage: 1 allocs, 0 frees, 40 bytes allocated
==26339== 
==26339== 40 bytes in 1 blocks are definitely lost in loss record 1 of 1
==26339==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==26339==    by 0x10865B: f (in /home/njthykkathu/SKA/UKSW-29/integration-prototype/sip/examples/valgrind/myprog)
==26339==    by 0x108679: main (in /home/njthykkathu/SKA/UKSW-29/integration-prototype/sip/examples/valgrind/myprog)
==26339== 
==26339== LEAK SUMMARY:
==26339==    definitely lost: 40 bytes in 1 blocks
==26339==    indirectly lost: 0 bytes in 0 blocks
==26339==      possibly lost: 0 bytes in 0 blocks
==26339==    still reachable: 0 bytes in 0 blocks
==26339==         suppressed: 0 bytes in 0 blocks
==26339== 
==26339== For counts of detected and suppressed errors, rerun with: -v
==26339== ERROR SUMMARY: 2 errors from 2 contexts (suppressed: 0 from 0)
```

Note - the process ID and the path would be different. 