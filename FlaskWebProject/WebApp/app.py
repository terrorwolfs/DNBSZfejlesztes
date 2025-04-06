from WebApp import create_app, db
from WebApp.models import User, Room, Booking, CheckIn, Invoice, ExtraService

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Room': Room, 'Booking': Booking, 'CheckIn': CheckIn, 'Invoice': Invoice, 'ExtraService': ExtraService}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
