import bluetooth

import blesync_server


class UARTService(blesync_server.Service):
    uuid = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")

    _tx = blesync_server.Characteristic(
        bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
        bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
    )

    _rx = blesync_server.Characteristic(
        bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
        bluetooth.FLAG_WRITE,
        buffer_size=100,
        append=True
    )

    characteristics = (_tx, _rx)

    on_message = _rx.on_message

    def send(self, conn_handle, message):
        self._tx.notify(conn_handle, message)
