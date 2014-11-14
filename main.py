#init
import pyb, gc

# 1.0 open, 0.0 closed
w_status = 1
#0 early, 1 late, 2 night, 3 manual
w_mode = 3

w_times = [[(19,0),(8,0)],[(19,0),(10,0)],[(7,0),(14,30)]]
#hardware
i2c = pyb.I2C(2, pyb.I2C.MASTER)
i2c.mem_write(4, 90, 0x5e)
touch = i2c.mem_read(1, 90, 0)[0]

s_up = pyb.Servo(1)
s_down = pyb.Servo(2)

lcd = pyb.LCD('Y')

rtc = pyb.RTC()

led_b = pyb.LED(1)
led_2 = pyb.LED(2)
#calibration
s_up.angle(-12)

def use_btn_w_servo(servo,duration=8000,inverse=False):
    if inverse:
        end_pos = -30
    else:
        end_pos = 30
    neut = servo.angle()
    servo.angle(neut - end_pos)
    pyb.delay(duration)
    servo.angle(neut + end_pos)
    pyb.delay(2000)
    servo.angle(neut)
    return True

loop = True
while loop:
    #led_2.toggle()
    pyb.delay(500)
    now = rtc.datetime()[4:6]
    touch = i2c.mem_read(1, 90, 0)[0]

    if touch == 5:
        if w_mode == 3:
            w_mode = 0
        else:
            w_mode +=1
    elif touch == 7:
        loop = False

    if w_mode == 3:
        if touch == 8:
            use_btn_w_servo(s_up)
        if touch == 10:
            use_btn_w_servo(s_down, inverse=True)
    else:
        t_border = w_times[w_mode]
        if ((t_border[0][0] < t_border[1][0]) and(t_border[0][0] <= now[0] <= t_border[1][0])) or \
            ((t_border[0][0] > t_border[1][0]) and (t_border[0][0] <= now[0] or now[0] <= t_border[1][1])):
            #hours only, ignoring minutes for now
            led_b.toggle()
            if w_status == 1:
                #toggle window blind
                use_btn_w_servo(s_down, inverse=True)
                w_status = 0
        else:
            led_b.off()
            if w_status == 0:
                #toggle window blind
                use_btn_w_servo(s_up)
                w_status = 1
    lcd.write('Mode:' + str(w_mode) + ' State:' + str(w_status) +' \n')
    lcd.write('Time: ' + str(now[0]) + ':' + str(now[1]) +'\n')
    if w_mode < 3:
        lcd.write('Closed ' + str(t_border[0][0])  + "h-"+str(t_border[1][0]) + 'h \n')
    else:
        lcd.write('-------- \n')
    lcd.write('-------- \n')
