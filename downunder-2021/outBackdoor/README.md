For this challenge, we are presented with a single binary named "outBackdoor". When we run it, we get the following output and it hangs waiting for user input.

```
$ ./outBackdoor 

Fool me once, shame on you. Fool me twice, shame on me.

Seriously though, what features would be cool? Maybe it could play a song?
```

Here's the disassembly of the main() function.

```asm
 66: int main (int argc, char **argv, char **envp);
│           ; var char *s @ rbp-0x10
│           0x00401195      55             push rbp
│           0x00401196      4889e5         mov rbp, rsp
│           0x00401199      4883ec10       sub rsp, 0x10
│           0x0040119d      b800000000     mov eax, 0
│           0x004011a2      e8abffffff     call sym.buffer_init
│           0x004011a7      488d3d5a0e00.  lea rdi, str._nFool_me_once__shame_on_you._Fool_me_twice__shame_on_me. ; 0x402008 ; "\nFool me once, shame on you. Fool me twice, shame on me." ; const char *s
│           0x004011ae      e87dfeffff     call sym.imp.puts           ; int puts(const char *s)
│           0x004011b3      488d3d8e0e00.  lea rdi, str._nSeriously_though__what_features_would_be_cool__Maybe_it_could_play_a_song_ ; 0x402048 ; "\nSeriously though, what features would be cool? Maybe it could play a song?" ; const char *s
│           0x004011ba      e871feffff     call sym.imp.puts           ; int puts(const char *s)
│           0x004011bf      488d45f0       lea rax, [s]
│           0x004011c3      4889c7         mov rdi, rax                ; char *s
│           0x004011c6      b800000000     mov eax, 0
│           0x004011cb      e890feffff     call sym.imp.gets           ; char *gets(char *s)
│           0x004011d0      b800000000     mov eax, 0
│           0x004011d5      c9             leave
└           0x004011d6      c3             ret
```

In the prologue we can see that it's making 16 bytes (0x10) of space on the stack. Next it calls a buffer_init() function which disables buffering on standard input, standard output, and standard error which is commonly done in these types of problems. Next, it prints out the two lines we saw when we ran it by calling puts() twice. Next it calls gets() to read input from the user and stores it starting at the 16 byte space it made on the stack. Finally it sets the return code (eax) to 0 and returns.

Interestingly, there's another function in this binary named "outBackdoor". Here's it's disassembly:

```asm
┌ 36: sym.outBackdoor ();
│           0x004011d7      55             push rbp
│           0x004011d8      4889e5         mov rbp, rsp
│           0x004011db      488d3db60e00.  lea rdi, str._n_nW...w...Wait__Who_put_this_backdoor_out_back_here_ ; 0x402098 ; "\n\nW...w...Wait? Who put this backdoor out back here?" ; const char *s
│           0x004011e2      e849feffff     call sym.imp.puts           ; int puts(const char *s)
│           0x004011e7      488d3ddf0e00.  lea rdi, str._bin_sh        ; 0x4020cd ; "/bin/sh" ; const char *string
│           0x004011ee      b800000000     mov eax, 0
│           0x004011f3      e858feffff     call sym.imp.system         ; int system(const char *string)
│           0x004011f8      90             nop
│           0x004011f9      5d             pop rbp
└           0x004011fa      c3             ret
```

This function prints out a message by calling puts() and then calls system(/bin/sh).

This is a typical "ret2win" style. The gets() call in main allows us to fill the 16 byte buffer and then overwrite the stored ebp and stored rip. This binary doesn't contain a stack canary, so we don't have to worry about crashing if we overwrite that in the process. In order to overwrite the stored rip, we'll need to send 16 bytes to fill the buffer, 8 bytes to overwrite the stored rbp, and 8 bytes to overwrite the stored rip. The contents of rbp don't matter here, so we can just send 24 bytes of padding followed by the little-endian representation of the address of the "outBackdoor" function.

There's a final challenge here which is that some modern linux systems have libc versions which crash if the stack isn't 16-byte aligned when you call a library function due to using some optimized instructions which have that requirement. In this case, if we return to outBackdoor() immediately, our stack pointer is not 16-byte aligned and the exploit will fail against the remote server. The easiest workaround for this problem is typically to just overwrite the saved rip with a pointer to a "ret" instruction which will advance the stack pointer by eight bytes therefore making it 16-byte aligned and then returning to the function we're trying to call.

Here's the output when run against the challenge server:

```
$ python outBackdoor.py REMOTE
[+] Opening connection to pwn-2021.duc.tf on port 31921: Done
[*] Loaded 14 cached gadgets for './outBackdoor'
[*] Switching to interactive mode


W...w...Wait? Who put this backdoor out back here?
$ cat flag.txt
DUCTF{https://www.youtube.com/watch?v=XfR9iY5y94s}
```

