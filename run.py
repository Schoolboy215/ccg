# Run a test server.
from app import app
app.run(host='0.0.0.0', debug=True)
#app.run(host='0.0.0.0', port=5000, debug=True)