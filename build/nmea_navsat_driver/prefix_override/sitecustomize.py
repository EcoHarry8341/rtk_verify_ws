import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/cat/rtk_verify_ws/install/nmea_navsat_driver'
