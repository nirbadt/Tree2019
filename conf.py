mqtt_config = {}

strip_len = 25
ring_len = 8

colors = {
    'black': (0, 0, 0),
    'red': (128, 0, 0),
    'blue': (0, 0, 128),
    'magenta': (128, 0, 128),
    'cyan': (0, 128, 128),
    'white': (255, 255, 255)
}

animation_rise_duration_ms = 2000
animation_rewind_duration_ms = 1000
animation_breath_period_ms = 2000
animation_rainbow_period_ms = 3000
animation_rotation_period_ms = 500

pins = {
    'touch': 27,
    'strip': 21,
    'mp3_TX': 17,
    'mp3_RX': 16,
    'ring': 22
}
touch_threshold = 300
touch_release_timeout_ms = 500


mqtt_config['clean'] = False
mqtt_config['server'] = 'mqtt://mqtt.pndsn.com'
