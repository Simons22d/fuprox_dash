# learn is the package
from fuprox import app
import eventlet
import eventlet.wsgi

port = 3000
if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('', port)), app)



