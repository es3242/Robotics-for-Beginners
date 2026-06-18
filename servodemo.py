from microbit import *
import machine
from time import sleep_us

MOTOR_I2C_ADDR = 0x30


def motor_driver_found():
    try:
        return MOTOR_I2C_ADDR in i2c.scan()
    except OSError:
        return False


class Mecanum_Car_Driver_V2:
    def __init__(self):
        self.add = MOTOR_I2C_ADDR
        self.set_all_pwm(0)
        self.lastEchoDuration = 0
        sleep(5)

    def set_pwm(self, channel, value):
        i2c.write(self.add, bytearray([channel, value & 0xFF]), repeat=False)

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

    def get_distance(self):
        try:
            pin15.write_digital(0)
            sleep_us(2)
            pin15.write_digital(1)
            sleep_us(10)
            pin15.write_digital(0)

            t = machine.time_pulse_us(pin16, 1, 35000)
        except OSError:
            return 999

        if t <= 0 and self.lastEchoDuration > 0:
            t = self.lastEchoDuration
        elif t > 0:
            self.lastEchoDuration = t
        else:
            return 999

        return round(t * 0.013)


if not motor_driver_found():
    display.show(Image.NO)
    sleep(1000)
    display.scroll("NO 30")
    while True:
        sleep(1000)


class Servo:
    def __init__(self, pin, freq=50, min_us=600, max_us=2400, angle=180):
        self.min_us = min_us
        self.max_us = max_us
        self.freq = freq
        self.angle = angle
        self.pin = pin
        self.pin.set_analog_period(round((1 / self.freq) * 1000))

    def write_us(self, us):
        us = min(self.max_us, max(self.min_us, us))
        duty = round(us * 1024 * self.freq // 1000000)
        self.pin.write_analog(duty)
        sleep(300)
        self.pin.write_analog(0)

    def write_angle(self, degrees):
        degrees = max(0, min(self.angle, degrees))
        total_range = self.max_us - self.min_us
        us = self.min_us + total_range * degrees // self.angle
        self.write_us(us)

mecanumCar = Mecanum_Car_Driver_V2()
servo = Servo(pin14)
servo.write_angle(90)

running = False
fast_speed = 150
turn_delay = 450
forward_speed = 150
obstacle_distance = 15


def forward():
    mecanumCar.Motor_Upper_L(1, forward_speed)
    mecanumCar.Motor_Lower_L(0, forward_speed)
    mecanumCar.Motor_Upper_R(1, forward_speed)
    mecanumCar.Motor_Lower_R(0, forward_speed)


def turnright():
    mecanumCar.Motor_Upper_L(1, fast_speed)
    mecanumCar.Motor_Lower_L(0, fast_speed)
    mecanumCar.Motor_Upper_R(0, 0)
    mecanumCar.Motor_Lower_R(0, 0)


def turnleft():
    mecanumCar.Motor_Upper_L(0, 0)
    mecanumCar.Motor_Lower_L(0, 0)
    mecanumCar.Motor_Upper_R(1, fast_speed)
    mecanumCar.Motor_Lower_R(0, fast_speed)


def stop():
    mecanumCar.stop_all()


while True:
    if button_a.was_pressed():
        running = not running
        if running:
            display.show(Image.YES)
            servo.write_angle(90)
        else:
            display.show(Image.NO)
            stop()

    while running:
        if button_a.was_pressed():
            running = False
            display.show(Image.NO)
            stop()
            break

        distance = mecanumCar.get_distance()

        if distance < obstacle_distance:
            stop()
            sleep(200)

            servo.write_angle(160)
            sleep(200)
            distance_l = mecanumCar.get_distance()

            servo.write_angle(20)
            sleep(200)
            distance_r = mecanumCar.get_distance()

            servo.write_angle(90)
            sleep(100)

            if distance_l > distance_r:
                turnleft()
                sleep(turn_delay)
            else:
                turnright()
                sleep(turn_delay)

            stop()
            sleep(50)
        else:
            forward()

        sleep(10)
