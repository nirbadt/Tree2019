
from machine import Pin, TouchPad, Timer, Neopixel
import network
import dfplayermini
from animation_controller import AnimationController
import conf
import conf_tree

touch = TouchPad(Pin(conf.pins['touch']))
strip = AnimationController('strip')
ring = AnimationController('ring')
music = dfplayermini.Player(pin_TX=conf.pins['mp3_TX'], pin_RX=conf.pins['mp3_RX'])


mqtt_topic_subscribe = conf_tree.remote['name'] + '_status'
mqtt_topic_publish = conf_tree.local['name'] + '_status'


touch_local_prev = touch_local_current = touch_remote_prev = touch_remote_current = state_local = state_remote = 0
show_rainbow = show_idle = False
track_playing = track_to_play = False


def mqtt_received(mqtt_name, topic_data_length, topic_data):
    print("received:", topic_data)
    global touch_remote_current
    if topic_data[1] == str.encode(mqtt_topic_subscribe):
        touch_remote_current = int(topic_data[2])


def mqtt_subscribed(mqtt_name, topic):
    print("subscribed to", topic)


def mqtt_published(mqtt_name, publish_result):
    print("published:", publish_result)


def mqtt_disconnected(mqtt_name):
    print("lost connection to mqtt")
    ring.animate('offline')


def mqtt_connected(mqtt_name):
    print("Let's tree!")
    ring.animate('breath')


def publish_status(status):
    try:
        print("mqtt.publish disabled")
        # mqtt.publish(mqtt_topic_publish, status)
    except:
        print("mqtt is not connected")
        return


def check_touch(timer):
    global touch_local_current
    try:
        value = touch.read()
        touch_local_current = 1 if value < conf.touch_threshold else 0
    except:
        print("error in reading ", value)


def toggleRemoteStatus(timer):
    global touch_remote_current
    touch_remote_current = 1 - touch_remote_current

def process_strip(timer):
    strip.process()
    
    
def process_ring(timer):
    ring.process()




def main(timer):
    global touch_local_prev, touch_local_current, touch_remote_prev, touch_remote_current, state_local, state_remote
    global show_rainbow, show_idle, track_playing
    global track_playing, track_to_play
    
    
    if touch_local_prev is not touch_local_current:
        print("touch is happened")        
        publish_status(touch_local_current)


    state_local = int(str(touch_local_prev) + str(touch_local_current), 2)
    state_remote = int(str(touch_remote_prev) +
                       str(touch_remote_current), 2)

    if state_remote == 1:  # call initiated
        # odd_even = 1
        strip.animate('rise', [1, 'start', Neopixel.MAGENTA])
        ring.animate('rotate', ['cw', Neopixel.MAGENTA])
        show_idle = False
        track_to_play = 3
    elif state_remote == 2:  # call end
        strip.animate('rise', [1, 'rewind'])  # odd_even = 1
        ring.animate('rotate', ['ccw', Neopixel.MAGENTA])
        show_rainbow = False

    if state_local == 1:  # call initiated
        strip.animate('rise', [0, 'start', Neopixel.CYAN])
        ring.animate('rotate', ['cw', Neopixel.CYAN])
        track_to_play = 1
        show_idle = False
    elif state_local == 2:  # call end
        strip.animate('rise', [0, 'rewind'])
        ring.animate('rotate', ['ccw', Neopixel.CYAN])
        track_to_play = 2
        show_rainbow = False

    if strip.rise_animation_finished():
        if state_local == state_remote == 3:
            if not show_rainbow:
                show_rainbow = True
                strip.animate('rainbow')
                ring.animate('rainbow')
                track_to_play = 4
        elif state_local == state_remote == 0:
            if not show_idle:
                print("turn off the lights")
                show_idle = True
                strip.animate('blank')
                ring.animate('breath')
                track_to_play = False
        elif state_local == 0 and state_remote == 3:
            track_to_play = 3
        elif state_remote == 0 and state_local == 3:
            track_to_play = 1

    if track_to_play is not track_playing:
        if track_to_play:
            pass
            music.play_track(track_to_play)
        else:
            pass
            music.stop()

    track_playing = track_to_play
    touch_local_prev = touch_local_current
    touch_remote_prev = touch_remote_current


# mqtt = False
# try:
#     mqtt = network.mqtt(conf_tree.local['name'], conf.mqtt_config['server'], clientid = conf_tree.wifi['client_id'],
#     connected_cb=mqtt_disconnected,
#     disconnected_cb=mqtt_connected,
#     subscribed_cb=mqtt_subscribed,
#     published_cb=mqtt_published,
#     data_cb=mqtt_received,
#     lwt_topic = mqtt_topic_publish,
#     lwt_msg = "0"
#     )
# except ValueError:
#     print("error, error")

# mqtt = network.mqtt(conf_tree.local['name'], conf.mqtt_config['server'], clientid = conf_tree.wifi['client_id'],
#     connected_cb=mqtt_disconnected,
#     disconnected_cb=mqtt_connected,
#     subscribed_cb=mqtt_subscribed,
#     published_cb=mqtt_published,
#     data_cb=mqtt_received,
#     lwt_topic = mqtt_topic_publish,
#     lwt_msg = "0"
#     )


# mqtt.start()
# mqtt.subscribe(mqtt_topic_subscribe)


tex = Timer(0)
tex.init(mode=tex.EXTBASE)

t1 = Timer(4)
t1.init(period=200, mode=t1.PERIODIC, callback=check_touch)

t2 = Timer(5)
t2.init(period=50, mode=t2.PERIODIC, callback=process_strip)
t3 = Timer(6)
t3.init(period=50, mode=t3.PERIODIC, callback=process_ring)

t4 = Timer(7)
t4.init(period=100, mode=t4.PERIODIC, callback=main)

t5 = Timer(8)
t5.init(period=20000, mode=t5.PERIODIC, callback=toggleRemoteStatus)
