from machine import Pin
import stm, pyb

@micropython.viper
def LED_flip(p):
    odrA = ptr16(stm.GPIOA + stm.GPIO_ODR)
    odrA[0] ^= 0b0000000000100000
    # PA5. You can flip as many PAx pins at once as you want
    a = odrA[0] & 32
    if(a>0):
        print("LED1 is on.")
    else:
        print("LED1 is off.")
    

@micropython.viper
def LED_on():
    odrA = ptr16(stm.GPIOA + stm.GPIO_ODR)
    odrA[0] |= 0b0000000000100000

LED_on()
USR = Pin(Pin.cpu.C13, mode=Pin.IN)
#LED1=Pin(Pin.cpu.A5, mode=Pin.OUT)
LED_on()
ledStatus = 1

def cback(p):
    #global ledStatus
    #ledStatus = 1-ledStatus
    #print("ledStatus is {}".format(ledStatus))
    #if ledStatus == 1:
        #LED1.on()
    #else:
        #LED1.off()
    LED_flip()
    print(p)
USR.irq(LED_flip, trigger=Pin.IRQ_FALLING)
