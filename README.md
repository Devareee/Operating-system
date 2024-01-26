# Operating system

## Проект гипотетической операционной системы, включающий в себя программу эмуляции файловой системы, планировщик процессов и командный интерпретатор.
На диске с файловой системой находится один раздел с проектируемой файловой системой. За ее основу взята файловая система «S5FS».
Ядро операционной системы состоит  трёх основных модулей: файловая подсистема; подсистема управления процессами и памятью; подсистема ввода-вывода.
Планирование процессов внутри очереди 0 осуществляется с использованием алгоритма RoundRobin (RR), а внутри очереди 1 – FirstComeFirstServe (FCFS).

## A hypothetical operating system project that includes a file system emulation program, a process scheduler, and a command interpreter.
The disk with the file system contains one partition with the projected file system. It is based on the S5FS file system.
The operating system kernel consists of three main modules: the file subsystem; process and memory management subsystem; input/output subsystem.
Processes within queue 0 are scheduled using the RoundRobin (RR) algorithm, and processes inside queue 1 are scheduled using FirstComeFirstServe (FCFS).
