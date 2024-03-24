from flask import Flask, session
from flask_session import Session


app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # Você pode usar outros tipos de armazenamento de sessão, como 'redis', se preferir
Session(app)

app.config['SECRET_KEY'] = '29cecf8afd6176f06bb3f55472d490d1'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'


from markethubfiles import routes

@app.before_request
def before_request():
    print("Usuário na sessão:", session.get('usuario_id'))