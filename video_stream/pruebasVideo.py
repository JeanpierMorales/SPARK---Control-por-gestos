from stream_handler import VideoStreamHandler

if __name__ == "__main__":
    def test_callback(data):
        print("Gesto detectado:", data)

    stream = VideoStreamHandler(test_callback)
    stream.start()
    #while True:
    #    input()
