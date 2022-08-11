import typing
import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, func, create_engine



class HttpError(Exception):

    def __init__(self, status_code: int, message: str or dict or list):
        self.status_code = status_code
        self.message = message

class CreateAd(pydantic.BaseModel):
    title: str
    text: str
    owner: str

class PatchAd(pydantic.BaseModel):
    title: typing.Optional[str]
    text: typing.Optional[str]

def validate(model, raw_data: dict):
    try:
        return model(**raw_data).dict()
    except pydantic.ValidationError as error:
        raise HttpError(400, error.errors())


app = Flask('app')

@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    response = jsonify({
        'status': 'error',
        'reason': error.message
    })
    response.status_code = error.status_code
    return response


PG_DSN = 'postgresql://postgres:admin@127.0.0.1/flask'

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Ad (Base):
    __tablename__ = 'ads'
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(String, nullable=False)


def get_ad(session: Session, ad_id: int):
    ad = session.query(Ad).get(ad_id)
    if ad is None:
        raise HttpError(404, 'user not found')
    return ad


Base.metadata.create_all(engine)


class AdView(MethodView):

    def get(self, ad_id):

        with Session() as session:
            ad = get_ad(session, ad_id)
            return jsonify({'title': ad.title,
                            'text': ad.text,
                            'owner': ad.owner,
                            'created_at': ad.created_at.isoformat()
                            })

    def post(self):

        validated = validate(CreateAd, request.json)
        with Session() as session:
            ad = Ad(title=validated['title'], text=validated['text'], owner=validated['owner'])
            session.add(ad)
            session.commit()
            return {'id': ad.id}

    def patch(self, ad_id):

        validated = validate(PatchAd, request.json)

        json_data = request.json
        with Session() as session:
            ad = get_ad(session, ad_id)
        if validated.get('title'):
            ad.title = validated['title']
        if validated.get('text'):
            ad.text = validated['text']
        session.add(ad)
        session.commit()
        return {'status': 'success'}

    def delete(self, ad_id):
        with Session() as session:
            ad = get_ad(session, ad_id)
            session.delete(ad)
            session.commit()
            return {'status': 'success'}


ad_view = AdView.as_view('ads')
app.add_url_rule('/ads/', view_func=ad_view, methods=['POST'])
app.add_url_rule('/ads/<int:ad_id>', view_func=ad_view, methods=['GET', 'PATCH', 'DELETE'])
app.run()
