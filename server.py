import pydantic
from typing import Type, Optional
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import Column, Integer, String, DateTime, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

app = Flask('app')


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({
        'status': 'error', 'message': error.message
    })
    response.status_code = error.status_code
    return response


DSN = 'postgresql://app:1234@127.0.0.1:5432/netology'

engine = create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# password_regex = re.compile(
#     "^(?=.*[a-z_])(?=.*[A-Z])(?=.*[@$!%*#?&_])[A-Za-z\d@$!%*#?&_]{8,200}$"
# )


class AdvertisementModel(Base):
    __tablename__ = 'advertisement'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(5000), nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(String(100), nullable=False)


Base.metadata.create_all(engine)


class CreateAdvertisementSchema(pydantic.BaseModel):
    title: str
    description: str
    owner: str

    @pydantic.validator('title')
    def check_title(cls, value: str):
        if len(value) > 100:
            raise ValueError('title must be less 100 chars')
        return value

    @pydantic.validator('description')
    def check_description(cls, value: str):
        if len(value) > 5000:
            raise ValueError('description must be less 5000 chars')
        return value

    @pydantic.validator('owner')
    def check_owner(cls, value: str):
        if len(value) > 100:
            raise ValueError('owner must be less 100 chars')
        return value


class PatchAdvertisementSchema(pydantic.BaseModel):
    title: Optional[str]
    description: Optional[str]
    owner: Optional[str]

    @pydantic.validator('title')
    def check_title(cls, value: str):
        if len(value) > 100:
            raise ValueError('title must be less 100 chars')
        return value

    @pydantic.validator('description')
    def check_description(cls, value: str):
        if len(value) > 5000:
            raise ValueError('description must be less 5000 chars')
        return value

    @pydantic.validator('owner')
    def check_owner(cls, value: str):
        if len(value) > 100:
            raise ValueError('owner must be less 100 chars')
        return value


def validate(data_to_validate: dict, validation_class: Type[CreateAdvertisementSchema] | Type[PatchAdvertisementSchema]):
    try:
        return validation_class(**data_to_validate).dict(exclude_none=True)
    except pydantic.ValidationError as err:
        raise HttpError(400, err.errors())


def get_by_id(item_id: int, orm_model: Type[AdvertisementModel], session: Session):
    orm_item = session.query(orm_model).get(item_id)
    if orm_item is None:
        raise HttpError(404, 'item not found')
    return orm_item


class AdvertisementView(MethodView):

    def get(self, adv_id: int):
        with Session() as session:
            advertisement = get_by_id(adv_id, AdvertisementModel, session)
            if advertisement is None:
                raise HttpError(404, 'user not found')
            return jsonify({
                'title': advertisement.title,
                'description': advertisement.description,
                'owner': advertisement.owner,
                'creation_time': advertisement.creation_time.isoformat()
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            new_advertisement = AdvertisementModel(**validate(json_data, CreateAdvertisementSchema))
            session.add(new_advertisement)
            session.commit()
        return jsonify({'status': 'ok', 'id': new_advertisement.id})

    def patch(self, adv_id: int):
        data_to_patch = validate(request.json, PatchAdvertisementSchema)
        with Session() as session:
            advertisement = get_by_id(adv_id, AdvertisementModel, session)
            for field, value in data_to_patch.items():
                setattr(advertisement, field, value)
            session.commit()
            return jsonify({'status': 'success'})

    def delete(self, adv_id: int):
        with Session() as session:
            advertisement = get_by_id(adv_id, AdvertisementModel, session)
            session.delete(advertisement)
            session.commit()
            return jsonify({'status': 'success'})


app.add_url_rule('/advertisement/<int:adv_id>', view_func=AdvertisementView.as_view('advertisement_get'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/advertisement/', view_func=AdvertisementView.as_view('advertisement'), methods=['POST'])

app.run()
