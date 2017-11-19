''' temperatureSensor.sh
    Turns on the devices bluetooth hardware / interface
    usage "./setupBluetooth.sh"

    Jamie Sweeney
    2017/18 Solo Project
'''

`sudo systemctl start bluetooth`
echo "turned on bluetooth"

`sudo hciconfig hci0 up`
echo "turned on bluetooth interface"
