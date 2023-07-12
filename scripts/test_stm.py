# test stm module

import stm
import pyb

# test storing a full 32-bit number
# turn on then off the A15(=yellow) LED
while True:
    BSRR = 0x18
    stm.mem32[stm.GPIOA + BSRR] = 0x0000a000 # 8 + 2 on yellow / red PA15/PA13
    stm.mem32[stm.GPIOA + BSRR] = 0x40000000 # 4 off green PA14
    stm.mem32[stm.GPIOB + BSRR] = 0x00100000 # blue off PB4
    pyb.delay(500)
    #print(hex(stm.mem32[stm.GPIOA + stm.GPIO_ODR] & 0x0000f000))
    stm.mem32[stm.GPIOA + BSRR] = 0xa0000000 # 8 + 2 off
    stm.mem32[stm.GPIOA + BSRR] = 0x00004000 # 4 on
    stm.mem32[stm.GPIOB + BSRR] = 0x00000010 # blue on
    #print(hex(stm.mem32[stm.GPIOA + stm.GPIO_ODR] & 0x0000f000))
    pyb.delay(500)
