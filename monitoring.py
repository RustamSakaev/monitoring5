from app import create_app, db
from app.models import User, District

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

@app.context_processor
def inject_districts():
    return dict(districts=District.query.all())