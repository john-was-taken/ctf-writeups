For this challenge, we are presented with a challenge binary named "write-what-where" as well as a copy of the libc which is in use on the target system. When we run the challenge binary, we are asked for what we would like to write and where we would like to write it. In this example, the test input I provided resulted in the binary segfaulting.

```
$ ./write-what-where 
write
what?
A
where?
A
Segmentation fault
```

Here's the disassembly of the main() function.

```asm
┌ 162: int main (int argc, char **argv, char **envp);
│           ; var int64_t var_30h @ rbp-0x30
│           ; var void *buf @ rbp-0x24
│           ; var char *str @ rbp-0x20
│           ; var int64_t var_8h @ rbp-0x8
│           0x004011a9      55             push rbp
│           0x004011aa      4889e5         mov rbp, rsp
│           0x004011ad      4883ec30       sub rsp, 0x30
│           0x004011b1      64488b042528.  mov rax, qword fs:[0x28]
│           0x004011ba      488945f8       mov qword [var_8h], rax
│           0x004011be      31c0           xor eax, eax
│           0x004011c0      b800000000     mov eax, 0
│           0x004011c5      e89cffffff     call sym.init
│           0x004011ca      488d05330e00.  lea rax, str.write          ; 0x402004 ; "write"
│           0x004011d1      4889c7         mov rdi, rax                ; const char *s
│           0x004011d4      e857feffff     call sym.imp.puts           ; int puts(const char *s)
│           0x004011d9      488d052a0e00.  lea rax, str.what_          ; 0x40200a ; "what?"
│           0x004011e0      4889c7         mov rdi, rax                ; const char *s
│           0x004011e3      e848feffff     call sym.imp.puts           ; int puts(const char *s)
│           0x004011e8      488d45dc       lea rax, [buf]
│           0x004011ec      ba04000000     mov edx, 4                  ; size_t nbyte
│           0x004011f1      4889c6         mov rsi, rax                ; void *buf
│           0x004011f4      bf00000000     mov edi, 0                  ; int fildes
│           0x004011f9      e842feffff     call sym.imp.read           ; ssize_t read(int fildes, void *buf, size_t nbyte)
│           0x004011fe      488d050b0e00.  lea rax, str.where_         ; 0x402010 ; "where?"
│           0x00401205      4889c7         mov rdi, rax                ; const char *s
│           0x00401208      e823feffff     call sym.imp.puts           ; int puts(const char *s)
│           0x0040120d      488d45e0       lea rax, [str]
│           0x00401211      ba09000000     mov edx, 9                  ; size_t nbyte
│           0x00401216      4889c6         mov rsi, rax                ; void *buf
│           0x00401219      bf00000000     mov edi, 0                  ; int fildes
│           0x0040121e      e81dfeffff     call sym.imp.read           ; ssize_t read(int fildes, void *buf, size_t nbyte)
│           0x00401223      488d45e0       lea rax, [str]
│           0x00401227      4889c7         mov rdi, rax                ; const char *str
│           0x0040122a      e831feffff     call sym.imp.atoi           ; int atoi(const char *str)
│           0x0040122f      4898           cdqe
│           0x00401231      488945d0       mov qword [var_30h], rax
│           0x00401235      488d55dc       lea rdx, [buf]
│           0x00401239      488b45d0       mov rax, qword [var_30h]
│           0x0040123d      8b12           mov edx, dword [rdx]
│           0x0040123f      8910           mov dword [rax], edx
│           0x00401241      bf00000000     mov edi, 0                  ; int status
└           0x00401246      e825feffff     call sym.imp.exit           ; void exit(int status)
```

In the prologue we can see that it's making 48 bytes (0x30) of space on the stack and then storing a canary value at the end of that space, although this value is not used because main doesn't return. Next it calls an init() function which disables buffering on standard input and standard output which is commonly done in these types of problems. Next, it prints out the two lines we saw when we ran it by calling puts() twice. Next it calls read() to read 4 bytes of input from the user and stores it starting at rbp-0x24. Next it calls puts() to print another prompt line and then calls read() again to read 9 bytes of input from the user and stores it starting at rbp-0x20. Next it passes the buffer it just read into to atoi(). It then writes the four bytes it read into rbp-0x24 to the address it decoded by calling atoi() on the second user input. Finally, it sets the return code (edi) to zero and calls exit().

The challenge binary is not a position independent executable (PIE) and has only partial relocation read-only mitigations (Partial RELRO). Because of this, it's possible for us to overwrite entires in the global offset table (GOT), however we are somewhat limited because we don't have a way to leak any addresses at this point. We also have an immediate concern which is that the binary is about to call exit() so we should overwrite that first. Since exit() hasn't been previously called, it's GOT entry should point to the procedure linkage table (PLT) code which resolves the real address. We can confirm that by setting a breakpoint at the instruction which performs the write (main+150) and inspect the GOT:

```
pwndbg> x/xg 0x404000
0x404000:       0x0000000000403e10
pwndbg> 
0x404008:       0x00007ffff7ffe180
pwndbg> 
0x404010:       0x00007ffff7fe8610
pwndbg> 
0x404018 <puts@got.plt>:        0x00007ffff7e5d5f0
pwndbg> 
0x404020 <read@got.plt>:        0x00007ffff7ed5e80
pwndbg> 
0x404028 <setvbuf@got.plt>:     0x00007ffff7e5dcd0
pwndbg> 
0x404030 <atoi@got.plt>:        0x00007ffff7e23fa0
pwndbg> 
0x404038 <exit@got.plt>:        0x0000000000401076
pwndbg> 
0x404040:       0x0000000000000000
```

A typical approach here would be to write the address of main() over the address of the PLT lookup routine, but if we do that in this case we still don't have a leak and because of address space layout randomization (ASLR) of libc addresses, we would be stuck. Interestingly, if we look at what happens between the write and the call to exit(), we notice that a pointer to where we wrote remains in rax. This, combined with the standard pattern of loading a pointer into rax and then moving it into rdi to pass to puts() gives up the leak we were looking for if we instead overwite the GOT address of exit() with the address of main+40. The net impact of this approach is that instead of exiting the program we will loop back through a second time. Instead of printing "write" the second time, we will leak a "string" pointed to by the address we wrote to. Since c doesn't actually define a string type, puts() will leak data up to the first null bytes (\x00).

The first thing we leak will just be the address of got.exit which we know already since this binary isn't PIE, however we can now consider how we can leak something more useful. Looking at the data in the GOT above, we would ideally like to leak any of the 0x00007f.. addresses, but we have a problem which is that we're only able to leak the address which we're writing to, so we'd overwrite the value before leaking it which isn't helpful. We also can't overwrite a value we don't care about such as got.setvbuf because we can only write four bytes and the leak is going to interpret the null bytes in those addresses as the end of the string. 

The trick here is to overwrite the top portion of an address we no longer need. I chose to use _dl_runtime_resolve_xsavec which is at 0x404010 since we've already resolved all the imported function addresses and won't need to call that again. By overwriting the null bytes at the top of that address, we can then leak the bytes we wrote followed by the resolved address of got.puts. Once we have that address, we can use the copy of the libc binary from the target system to calculate the address of system().

At this point, all that's left to do is to overwrite got.atoi with the address of system because the buffer which the second read() writes into is passed as the first arugment to atoi() and supplying "/bin/sh\x00" as the contents of that buffer on the next run.

There's a final challenge here which is that some modern linux systems have libc versions which crash if the stack isn't 16-byte aligned when you call a library function due to using some optimized instructions which have that requirement. In this case, if we return to system() at this point, our stack pointer is not 16-byte aligned and the exploit will fail against the remote server. The easiest workaround in this specific case is to just overwite got.exit a second time before we overwrite got.atoi.

Here's the output when run against the challenge server:

```
$ python write-what-where.py REMOTE
[+] Opening connection to pwn-2021.duc.tf on port 31920: Done
[*] Leaked puts address (0x7f84b02019d0)
[*] Calculated system address (0x7f84b01d0a60)
[*] Switching to interactive mode

$ cat flag.txt
DUCTF{arb1tr4ry_wr1t3_1s_str0ng_www}
```

