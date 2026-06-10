"""Entry point for the Collaborative Research Datasets and Curators Application.

Author:      Leonardo Andres Sandino Acosta
Project:     IT 566 Final Project
Date:        June 10, 2026
Class:       IT-566: Computer Scripting Techniques
"""

import json
from argparse import ArgumentParser
from datasets_and_curators.presentation_layer.user_interface import UserInterface


def main():
    """Application entry point."""
    args = configure_and_parse_commandline_arguments()

    config = None
    if args.configfile:
        with open(args.configfile, 'r') as f:
            config = json.loads(f.read())

    ui = UserInterface(config)
    ui.start()


def configure_and_parse_commandline_arguments():
    """Configure and parse command-line arguments."""
    parser = ArgumentParser(
        prog='main.py',
        description='Start the Collaborative Research Datasets and Curators application.',
        epilog='Author: Leonardo Sandino | IT 566 Final Project SU26')

    parser.add_argument(
        '-c', '--configfile',
        help="Path to the application configuration JSON file.",
        required=True)

    return parser.parse_args()


if __name__ == "__main__":
    main()
