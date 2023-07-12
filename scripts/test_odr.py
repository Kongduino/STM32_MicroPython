import pyb

@micropython.viper
def flip():
    odrA = ptr16(stm.GPIOA + stm.GPIO_ODR)
    odrA[0] ^= 0b0000000000100000

