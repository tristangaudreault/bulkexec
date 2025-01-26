import argparse
import logging
from collections.abc import Iterable
import numpy as np
from typing import Generator
from contextlib import nullcontext
import subprocess
import csv

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parses command-line arguments relevant to this module.

    Returns:
        argparse.Namespace: The parsed known arguments.
        list[str]: The unknown arguments.
    """
    parser = argparse.ArgumentParser(description="Bulk execution parser")
    parser.add_argument(
        "--log",
        type=str.upper,
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="set the logging level (default: WARNING)",
    )
    parser.add_argument(
        "--log-format",
        default="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        help="set the logging format",
    )
    parser.add_argument("--output", "-o")

    return parser.parse_known_args()


def configure_logging(log_level: str, log_format: str):
    """Configures the logging system with the specified logging level and sets the format.

    Args:
        log_level (str): The desired logging level which can be "DEBUG", "INFO", "WARNING", "ERROR" or "CRITICAL"
        log_format (str): The desired logging format.
    """
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format=log_format,
    )


def generate_commands(unknown_args: list[str]) -> Generator[list[str], None, None]:
    """Evaluate command-line arguments and expand iterables to generate combinations.

    Args:
        argv (list): Command-line arguments as strings.

    Yields:
        Iterable[list]: List of arguments with iterables expanded.
    """
    evaluated_args = unknown_args[:]
    iterables = {}
    max_length = 1

    for idx, arg in enumerate(unknown_args):
        try:
            # Safely evaluate the argument
            value = eval(
                arg,
                {"__builtins__": None},
                {"n": max_length, "range": range, "repeat": np.repeat},
            )
            logger.debug(f'Evaluated "{arg}" to "{value}')

            if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                iterables[idx] = value
                max_length = max(len(value), max_length)
            else:
                evaluated_args[idx] = str(value)

        except Exception as e:
            # Leave the argument unchanged if evaluation fails
            logger.debug(
                f'Failed to evaluate argument "{arg}", raised exception: "{e}". If "{arg}" is not a python expression then this failure is intended.'
            )

    # Generate all combinations
    for i in range(max_length):
        for idx, iterable in iterables.items():
            evaluated_args[idx] = str(iterable[i % len(iterable)])
        yield evaluated_args


def handle_process_output(idx: int, process, csvwriter=None):
    """Process the output from a subprocess, logging it and optionally writing it to a CSV.

    Args:
        idx (int): The index of the subprocess.
        process: The subprocess.
        csvwriter: The optional CSV writer. If passed then the subprocess output will be written to it.
    """
    stdout, stderr = process.communicate()
    decoded_stdout = stdout.decode("utf-8")
    decoded_stderr = stderr.decode("utf-8")

    logger.info(
        f'Process {idx} exited with code {
            process.returncode} and output: "{decoded_stdout}"'
    )
    print(decoded_stdout, end="")
    if stderr:
        logger.error(
            f'Error code {process.returncode} from process {idx}: "{decoded_stderr}"'
        )

    if csvwriter:
        row = process.args + [
            decoded_stdout,
            decoded_stderr,
            process.returncode,
        ]
        csvwriter.writerow(row)


def execute_commands(
    unknown_args: list[str], commands: list[list[str]], output_file: str | None = None
):
    """
    Executes a list of shell commands as subprocesses, optionally logging the results to a CSV file.

    Args:
        unknown_args (list[str]): Raw command arguments to include in the CSV header.
        commands (list[list[str]]): A list of commands, where each command is represented as a list of strings.
        output_file (str | None): Path to a CSV file for logging the results. If None, results are not written to a file.
    """
    processes = []
    with (
        open(output_file, "w", newline="") if output_file else nullcontext()
    ) as csvfile:
        if output_file:
            csvwriter = csv.writer(csvfile)
            header = unknown_args + ["stdout", "stderr", "returncode"]
            csvwriter.writerow(header)
        else:
            csvwriter = None

        for idx, command in enumerate(commands):
            logger.debug(f'Launching process {idx} with command: "{" ".join(command)}"')

            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )
            processes.append(process)

        for idx, process in enumerate(processes):
            handle_process_output(idx, process, csvwriter)


def main():
    """Main entry point for the bulkexec module.
    Parses command-line arguments, configures logging, generates commands,
    and executes them with optional logging to a CSV file.
    """
    known_args, unknown_args = parse_arguments()
    configure_logging(known_args.log, known_args.log_format)

    logger.debug(f"Known arguments: {known_args}")
    logger.debug(f"Unknown arguments: {unknown_args}")
    commands = generate_commands(unknown_args)
    execute_commands(unknown_args, commands, known_args.output)


if __name__ == "__main__":
    main()
