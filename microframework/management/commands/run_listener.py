from nameko.cli import run
import argparse
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

log = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_system_checks = False

    def handle(self, *args, **options):
        AMQP_URI = 'pyamqp://guest:guest@172.17.0.5'
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
        if not hasattr(settings, 'MICROFRAMEWORK_SERVICE_CLASS'):
            log.error('You need to define MICROFRAMEWORK_SERVICE_CLASS in django settings')
            return False
        args = parser.parse_args(["--broker", AMQP_URI, "example.service:ListenerService"])

        run.main(args)
