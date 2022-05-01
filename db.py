import mongoengine as me

def connect(name, host, port, **kwargs):
    me.connect(name, host=host, port=port, **kwargs)

class Note(me.Document):
    text = me.StringField(required=True, max_length=1024)

class User(me.Document):
    name = me.StringField(required=True)
    user_id = me.IntField(required=True)
    notes = me.ListField(me.ReferenceField(Note))
    timezone = me.StringField(default='Europe/Moscow')