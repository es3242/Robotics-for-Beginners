from microbit import *


MOTOR_I2C_ADDR = 0x30
MOTOR_I2C_ADDR = 0x30
motor_ok = True
sensor_ok = True

def motor_driver_found():
    try:
        return MOTOR_I2C_ADDR in i2c.scan()
    except Exception:
        return False


class Mecanum_Car_Driver_V2:
    def __init__(self):
        self.add = MOTOR_I2C_ADDR
        self.set_all_pwm(0)
        sleep(5)

    def set_pwm(self, channel, value):
        global motor_ok
        if not motor_ok:
            return
        try:
            i2c.write(self.add, bytearray([channel, value & 0xFF]), repeat=False)
        except Exception:
            motor_ok = False

    def set_all_pwm(self, value):
        for ch in range(1, 9):
            self.set_pwm(ch, value)

    def Motor_Upper_L(self, direction, speed):
        self.set_pwm(1, 0 if direction else speed)
        self.set_pwm(2, speed if direction else 0)

    def Motor_Lower_L(self, direction, speed):
        self.set_pwm(8, 0 if direction else speed)
        self.set_pwm(7, speed if direction else 0)

    def Motor_Upper_R(self, direction, speed):
        self.set_pwm(3, 0 if direction else speed)
        self.set_pwm(4, speed if direction else 0)

    def Motor_Lower_R(self, direction, speed):
        self.set_pwm(6, 0 if direction else speed)
        self.set_pwm(5, speed if direction else 0)

    def stop_all(self):
        self.set_all_pwm(0)


if not motor_driver_found():
    display.show(Image.NO)
    sleep(1000)
    display.scroll("NO 30")
    while True:
        sleep(1000)


mecanumCar = Mecanum_Car_Driver_V2()


display.show(Image.YES)
sleep(1000)
display.clear()

runA = False
runB = False
def forward():
    mecanumCar.Motor_Upper_L(1, 100)
    mecanumCar.Motor_Lower_L(0, 100)
    mecanumCar.Motor_Upper_R(1, 100)
    mecanumCar.Motor_Lower_R(0, 100)

def backward():
    mecanumCar.Motor_Upper_L(0, 100)
    mecanumCar.Motor_Lower_L(1, 100)
    mecanumCar.Motor_Upper_R(0, 100)
    mecanumCar.Motor_Lower_R(1, 100)

def stop():
    mecanumCar.Motor_Upper_L(0, 0)
    mecanumCar.Motor_Lower_L(0, 0)
    mecanumCar.Motor_Upper_R(0, 0)
    mecanumCar.Motor_Lower_R(0, 0)


def left():
    mecanumCar.Motor_Upper_L(0, 100)
    mecanumCar.Motor_Lower_L(1, 100)
    mecanumCar.Motor_Upper_R(1, 100)
    mecanumCar.Motor_Lower_R(0, 100)


def right():
    mecanumCar.Motor_Upper_L(1, 100)
    mecanumCar.Motor_Lower_L(0, 100)
    mecanumCar.Motor_Upper_R(0, 100)
    mecanumCar.Motor_Lower_R(1, 100)
    
while True:
    if button_a.was_pressed():
        runA = True
        runB = False
        display.show(Image.ARROW_N)
        sleep(500)

    if button_b.was_pressed():
        runB = True
        runA = False
        display.show(Image.ARROW_S)
        sleep(500)

    while runA is True:
        # forward()
        left()
        
        sleep(10)
        if button_a.was_pressed():
            runA = False
            runB = False
            display.clear()
            stop()
        if button_b.was_pressed():
            runA = False
            runB = False
            display.clear()
            stop()

    while runB is True:
        # backward()
        right()
        
        sleep(10)
        if button_a.was_pressed():
            runA = False
            runB = False
            display.clear()
            stop()
        if button_b.was_pressed():
            runB = False
            runA = False
            display.clear()
            stop()

