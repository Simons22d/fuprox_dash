# learn is the package
from fuprox import app
import webbrowser

port = 3000
# webbrowser.open_new_tab(url=f"http://127.0.0.1:{port}/")
if __name__ == "__main__":
    app.run(debug=True,port=port)



