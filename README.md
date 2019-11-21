# django-microframework

Django microframework allows you for easy synchronization of database entities between multiple django instances.

# Requirements

* Python (3.6, 3.7, 3.8)
* Django (1.11, 2.0, 2.1, 2.2)

# Installation
    pip install django-microframework
    python manage.py migrate
Add `'microframework'` to your `INSTALLED_APPS` setting.

    INSTALLED_APPS = [
        ...
        'microframework',
    ]

# Usage
### Sender
In your models.py file:
```python
from microframework.sender import connect_signals
connect_signals([RegularModel, JSONModel, TreeModel, ForeignKeyModel], 'example_sender')
```
In your settings.py:
```python
MICROFRAMEWORK_AMQP_URI = 'pyamqp://guest:guest@172.17.0.5'
MICROFRAMEWORK_SENDER_NAME = 'example_sender'
```
### Listener
Create service.py file:
```python
from microframework.handler import DjangoObjectHandler, NamekoHandlerMeta
from example.models import RegularModel, JSONModel, TreeModel, ForeignKeyModel


class ListenerService(DjangoObjectHandler, metaclass=NamekoHandlerMeta):
    name = "listener_service"
    sender_name = "example_sender"
    synced_save_models = [RegularModel, JSONModel, TreeModel, ForeignKeyModel]
```
In your settings.py:
```python
MICROFRAMEWORK_SERVICE_CLASS = "example.service:ListenerService"
MICROFRAMEWORK_AMQP_URI = 'pyamqp://guest:guest@172.17.0.5'
```

In your manage.py - this needs to be put before anything else in your code:
```python
import eventlet
eventlet.monkey_patch()
```
In order to run listener service:
```
python manage.py run_listener
```

