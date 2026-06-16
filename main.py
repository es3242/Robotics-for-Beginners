from microbit import *


# The line sensors use pins that are shared with the LED display.
# Keep the display off while the robot is reading the line sensors.
display.off()

# The motor controller is found on I2C address 0x30.
MOTOR_I2C_ADDR = 0x30

# These flags let the program stop safely if hardware stops responding.
motor_ok = True
sensor_ok = True


def motor_driver_found():
    # Ask the micro:bit which I2C devices are connected.
    # If 0x30 is in the list, the motor board was found.
    try:
        return MOTOR_I2C_ADDR in i2c.scan()
    except Exception:
        return False


class Mecanum_Car_Driver_V2:
    # This class groups all motor-board commands in one place.
    def __init__(self):
        self.add = MOTOR_I2C_ADDR
        self.set_all_pwm(0)
        sleep(5)

    def set_pwm(self, channel, value):
        # Send one power value to one motor-board channel.
        global motor_ok
        if not motor_ok:
            return
        try:
            i2c.write(self.add, bytearray([channel, value & 0xFF]), repeat=False)
        except Exception:
            motor_ok = False

    def set_all_pwm(self, value):
        # Set all 8 motor channels to the same value.
        # Sending 0 to every channel stops the robot.
        for ch in range(1, 9):
            self.set_pwm(ch, value)

    def Motor_Upper_L(self, direction, speed):
        # Upper-left motor. Direction chooses which channel gets power.
        self.set_pwm(1, 0 if direction else speed)
        self.set_pwm(2, speed if direction else 0)

    def Motor_Lower_L(self, direction, speed):
        # Lower-left motor.
        self.set_pwm(8, 0 if direction else speed)
        self.set_pwm(7, speed if direction else 0)

    def Motor_Upper_R(self, direction, speed):
        # Upper-right motor.
        self.set_pwm(3, 0 if direction else speed)
        self.set_pwm(4, speed if direction else 0)

    def Motor_Lower_R(self, direction, speed):
        # Lower-right motor.
        self.set_pwm(6, 0 if direction else speed)
        self.set_pwm(5, speed if direction else 0)

    def stop_all(self):
        # Stop every motor.
        self.set_all_pwm(0)


if not motor_driver_found():
    # If the motor board is not found, show an error and stop here.
    display.show(Image.NO)
    sleep(1000)
    display.scroll("NO 30")
    while True:
        sleep(1000)


mecanumCar = Mecanum_Car_Driver_V2()

if not motor_ok:
    # E30 means the program found an I2C/motor-board problem.
    display.scroll("E30")
    while True:
        sleep(1000)

# Change this if your sensors read the line differently.
# If the robot follows the background instead of the line, try LINE_VALUE = 0.
LINE_VALUE = 1

# Tune these speeds for the track and battery level.
base_speed = 80
turn_speed = 100
slow_speed = 95

# running is False until Button A starts the robot.
running = False

# last_seen remembers where the line was last detected.
last_seen = "center"
debug_display = False


def on_line(value):
    # Convert a raw sensor value, 0 or 1, into True/False.
    return value == LINE_VALUE


def read_line_sensors():
    # Read left, center, and right line sensors.
    # pin3 = left, pin4 = center, pin10 = right.
    global sensor_ok
    try:
        return pin3.read_digital(), pin4.read_digital(), pin10.read_digital()
    except Exception:
        sensor_ok = False
        return 1, 1, 1


def forward():
    # Drive all four motors forward.
    mecanumCar.Motor_Upper_L(1, base_speed)
    mecanumCar.Motor_Lower_L(0, base_speed)
    mecanumCar.Motor_Upper_R(1, base_speed)
    mecanumCar.Motor_Lower_R(0, base_speed)


def slight_left():
    # Turn left by making the left side slower than the right side.
    mecanumCar.Motor_Upper_L(1, slow_speed)
    mecanumCar.Motor_Lower_L(0, slow_speed)
    mecanumCar.Motor_Upper_R(1, turn_speed)
    mecanumCar.Motor_Lower_R(0, turn_speed)


def slight_right():
    # Turn right by making the right side slower than the left side.
    mecanumCar.Motor_Upper_L(1, turn_speed)
    mecanumCar.Motor_Lower_L(0, turn_speed)
    mecanumCar.Motor_Upper_R(1, slow_speed)
    mecanumCar.Motor_Lower_R(0, slow_speed)


def search_left():
    # Spin/search left when the line was last seen on the left side.
    mecanumCar.Motor_Upper_L(0, 0)
    mecanumCar.Motor_Lower_L(0, 0)
    mecanumCar.Motor_Upper_R(1, turn_speed)
    mecanumCar.Motor_Lower_R(0, turn_speed)


def search_right():
    # Spin/search right when the line was last seen on the right side.
    mecanumCar.Motor_Upper_L(1, turn_speed)
    mecanumCar.Motor_Lower_L(0, turn_speed)
    mecanumCar.Motor_Upper_R(0, 0)
    mecanumCar.Motor_Lower_R(0, 0)


def stop():
    # A short name for stopping the robot.
    mecanumCar.stop_all()


def wait_for_button_release():
    # Prevent one button press from being counted multiple times.
    while button_a.is_pressed():
        sleep(20)
    sleep(100)


def show_state(text):
    # Left here for teaching/debugging, but not used because the display
    # shares pins with the line sensors.
    pass


def show_motor_error():
    # If motor commands fail while running, stop the robot.
    stop()


def run():
    # The main program loop.
    global LINE_VALUE, running, last_seen

    display.off()
    stop()
    sleep(500)

    while True:
        if button_a.was_pressed():
            # Button A toggles the robot between stopped and running.
            running = not running
            if running:
                display.off()
                sleep(100)
                left, center, right = read_line_sensors()
                if not sensor_ok:
                    running = False
                    stop()
                    continue
                last_seen = "center"
                stop()
            else:
                display.off()
            wait_for_button_release()
            if not running:
                stop()

        while running:
            # Press Button A again to stop the robot.
            if button_a.was_pressed():
                running = False
                display.off()
                wait_for_button_release()
                stop()
                break

            # Read the sensors once per loop.
            left, center, right = read_line_sensors()
            if not sensor_ok:
                running = False
                stop()
                break

            # Convert each sensor value into True/False.
            left_on = on_line(left)
            center_on = on_line(center)
            right_on = on_line(right)

            # Decide how to move based on which sensor sees the line.
            if center_on and not left_on and not right_on:
                # Line is centered, so drive forward.
                last_seen = "center"
                show_state("F")
                forward()
            elif left_on and center_on and not right_on:
                # Line is a little left, so correct left.
                last_seen = "left"
                show_state("L")
                slight_left()
            elif right_on and center_on and not left_on:
                # Line is a little right, so correct right.
                last_seen = "right"
                show_state("R")
                slight_right()
            elif left_on and not right_on:
                # Only the left sensor sees the line, so search left.
                last_seen = "left"
                show_state("L")
                search_left()
            elif right_on and not left_on:
                # Only the right sensor sees the line, so search right.
                last_seen = "right"
                show_state("R")
                search_right()
            elif left_on and center_on and right_on:
                # All sensors see the line, so keep moving forward.
                last_seen = "center"
                show_state("F")
                forward()
            else:
                # No sensor sees the line.
                # If we were centered last time, stop. If the line was last
                # seen left or right, turn that way to try to find it again.
                show_state("?")
                if last_seen == "center":
                    stop()
                elif last_seen == "left":
                    search_left()
                elif last_seen == "right":
                    search_right()
                else:
                    stop()

            if not motor_ok:
                # Stop if the motor board stops responding.
                running = False
                show_motor_error()

            # Small delay so the loop does not run too fast.
            sleep(20)

        if not running:
            # Keep the robot stopped while it is idle.
            stop()
            sleep(20)


try:
    run()
except Exception:
    # Last-resort safety: if anything unexpected happens, stop the robot.
    stop()
    display.off()
    while True:
        sleep(1000)
