from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
from pydantic import BaseModel
from jose import JWTError, jwt
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import MissingTokenError


Base = declarative_base()
app = FastAPI()
app.jwt = AuthJWT()


# Création de la classe modèle
class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    sender = Column(String(50))
    recipient = Column(String(50))
    content = Column(String(200))
    date_time = Column(DateTime)

# Création de la classe utilisateur
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    pseudo = Column(String(32), unique=True)
    password = Column(String(32))
    last_connection_date = Column(String(10))

class UserIn(BaseModel):
    pseudo: str
    password: str

class UserOut(BaseModel):
    message: str

# Connexion avec la base de données
engine = create_engine('mysql+pymysql://root:Lemonde2020@localhost:3308/justchat')
Base.metadata.create_all(engine)
# Création d'une session SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

# Définition du modèle de données pour la création d'un message
class MessageCreate(BaseModel):
    sender: str
    recipient: str
    content: str
    date_time: datetime

# Configuration de la gestion des autorisations CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clé secrète pour signer le JWT
SECRET_KEY = "Lemonde2020"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fonction pour générer un jeton JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Fonction pour vérifier le jeton JWT et renvoyer les données de l'utilisateur
def get_current_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        username = Authorize.get_jwt_subject()
        user = session.query(User).filter_by(pseudo=username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid user credentials")
        return user
    except MissingTokenError:
        raise HTTPException(status_code=401, detail="Missing token")

# Fonction permettant de vérifier que l'utilisateur existe dans la base de données
def verify_credentials(pseudo: str, password: str):
    try:
        user = session.query(User).filter_by(pseudo=pseudo, password=password).first()
        if user is not None:
            user.last_connection_date = datetime.now()
            session.commit()
            return user.id
        else:
            return -1
    except Exception as erreur:
        session.rollback()
        raise erreur

@app.post("/login")
def login(user: UserIn, Authorize: AuthJWT = Depends()):
    user_id = verify_credentials(user.pseudo, user.password)
    if user_id != -1:
        access_token = create_access_token({"sub": user.pseudo}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"message": "Connexion réussie", "access_token": access_token}
    else:
        raise HTTPException(status_code=401, detail="Pseudo ou mot de passe incorrect")

@app.post('/messages')
def create_message(message_data: MessageCreate):
    message = Message(
        sender=message_data.sender,
        recipient=message_data.recipient,
        content=message_data.content,
        date_time=message_data.date_time
    )
    session.add(message)
    session.commit()

    return {'message': 'Message envoyé avec succès', 'sender': message_data.sender}


@app.get('/messages/{username}')
def get_user_messages(username: str, current_user: User = Depends(get_current_user)):
    sent_messages = session.query(Message).filter_by(sender=username).all()
    received_messages = session.query(Message).filter_by(recipient=username).all()

    messages = {
        'sent_messages': [message.content for message in sent_messages],
        'received_messages': [message.content for message in received_messages]
    }

    return messages

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
