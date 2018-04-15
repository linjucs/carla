import argparse
import logging
import time

from agent import Agent
from CoRL_FCTL import CoRL_FCTL

from carla.client import make_carla_client, VehicleControl
from carla.tcp import TCPConnectionError
import numpy as np

class Manual(Agent):
    """
    Sample redefinition of the Agent,
    An agent that goes straight
    """
    def run_step(self, measurements, sensor_data, target):
        control = VehicleControl()
        control.throttle = 0.9

        return control


class AutoPilot(Agent):
    def run_step(self, measurements, sensor_data, target):
        control = measurements.player_measurements.autopilot_control
        control.steer = control.steer + np.random.triangular(-0.15, 0, 0.15)
        return control


if __name__ == '__main__':

    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='print some extra status information')
    argparser.add_argument(
        '-db', '--debug',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='localhost',
        help='IP of the host server (default: localhost)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-c', '--city-name',
        metavar='C',
        default='Town01',
        help='The town that is going to be used on benchmark'
        + '(needs to match active town in server, options: Town01 or Town02)')
    argparser.add_argument(
        '-n', '--log_name',
        metavar='T',
        default='test',
        help='The name of the log file to be created by the benchmark'
        )

    args = argparser.parse_args()
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    while True:
        try:
            with make_carla_client(args.host, args.port) as client:
                corl = CoRL_FCTL(city_name=args.city_name, name_to_save=args.log_name, save_data=True)
                agent = AutoPilot(args.city_name)
                results = corl.benchmark_agent(agent, client)
                corl.plot_summary_test()
                corl.plot_summary_train()

                break

        except TCPConnectionError as error:
            logging.error(error)
            time.sleep(1)
