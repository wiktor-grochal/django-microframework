from microframework.handler import DjangoObjectHandler, NamekoHandlerMeta
from example.models import RegularModel


class ListenerService(DjangoObjectHandler, metaclass=NamekoHandlerMeta):
    """
    This class generates handler methods in this
    fashion:

    @event_handler("wallet", "Client_saved")
    def client_saved(self, payload):
        self.object_saved_handler(payload, Client)

    You can override generated methods or create
    your own similarly.
    """
    name = "listener_service"
    sender_name = "example_sender"
    synced_save_models = [RegularModel]

