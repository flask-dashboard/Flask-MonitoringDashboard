
import requests
import sys

SIZE = 90000

if __name__ == '__main__':
    for i in range(SIZE):
        sys.stdout.write('\r{}/{}'.format(i+1, SIZE))
        sys.stdout.flush()
        try:
            requests.get('http://127.0.0.1:5000/')
        except Exception:
            pass
