import threading
import imagezmq

# Helper class implementing an IO deamon thread
class VideoStreamSubscriber:

    def __init__(self, port):
        # self.hostname = hostname
        self.port = port
        self._stop = False
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True
        self._thread.start()

    def receive(self, timeout=200.0):
        flag = self._data_ready.wait(timeout=timeout)
        if not flag:
            raise TimeoutError(
                "Timeout while reading from subscriber{}".format(self.port))
        self._data_ready.clear()
        return self._data

    def _run(self):
        stream_port ='tcp://*:{}'.format(self.port)
        receiver = imagezmq.ImageHub(stream_port)# imagezmq.ImageHub("tcp://{}:{}".format(self.hostname, self.port), REQ_REP=False)
        while not self._stop:
            self._data = receiver.recv_jpg()
            self._data_ready.set()
            receiver.send_reply(b'OK')
        receiver.close()

    def close(self):
        self._stop = True