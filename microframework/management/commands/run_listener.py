import argparse
import logging
import json
from multiprocessing import Process
from time import sleep
from nameko.cli import run
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.conf import settings
from microframework.handler import DjangoObjectHandler
from microframework.models import PendingObjects

log = logging.getLogger(__name__)
log.setLevel(getattr(settings, 'DJANGO_LOG_LEVEL', 'INFO'))


class Command(BaseCommand):
    requires_system_checks = False

    @staticmethod
    def sync_pending():
        """
        Sync left over pending objects in rare cases when two dependant messages
        are processed exactly at the same time and save_pending_objects gets executed
        before create_pending_objects inserts objects to DB.
        This could be also solved by locking entire PendingObjects table,
        but it looks like a much less elegant solution.
        """
        while True:
            try:
                pending_objects = PendingObjects.objects.all()
                for pending_object in pending_objects:
                    try:
                        pending_data = json.loads(pending_object.object_serialized)
                        model = pending_object.content_type.model_class()
                        DjangoObjectHandler.save_object(pending_data, model)
                        pending_object.delete()
                    except IntegrityError:
                        pass
            except Exception as e:
                log.error(e)
            sleep(getattr(settings, 'MICROFRAMEWORK_SYNC_PENDING_INTERVAL', 10))

    def handle(self, *args, **options):
        if not hasattr(settings, 'MICROFRAMEWORK_SERVICE_CLASS'):
            log.error('You need to define MICROFRAMEWORK_SERVICE_CLASS in django settings')
            return False
        if not hasattr(settings, 'MICROFRAMEWORK_AMQP_URI'):
            log.error('You need to define MICROFRAMEWORK_AMQP_URI in django settings')
            return False
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'services', nargs='+',
            metavar='module[:service class]',
            help='python path to one or more service classes to run')
        parser.add_argument(
            '--config', default='',
            help='The YAML configuration file')
        parser.add_argument(
            '--broker', default='pyamqp://guest:guest@localhost',
            help='RabbitMQ broker url')
        parser.add_argument(
            '--backdoor-port', type=int,
            help='Specify a port number to host a backdoor, which can be'
                 ' connected to for an interactive interpreter within the running'
                 ' service process using `nameko backdoor`.')

        args = parser.parse_args(["--broker",
                                  settings.MICROFRAMEWORK_AMQP_URI,
                                  settings.MICROFRAMEWORK_SERVICE_CLASS
                                  ])
        p = Process(target=self.sync_pending)
        p.start()
        run.main(args)
