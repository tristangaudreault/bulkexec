# BulkExec
BulkExec is a command-line python argument evaluator that iterates through iterable arguments to launch multiple commands with different argument combinations.

## Installation
BulkExec can be installed directly from PyPI:
```bash
pip install bulkexec
```

## Usage
BulkExec evaluates every string argument as a Python expression. If the argument is not a valid Python expression then the argument is not modified. If the argument is a valid Python expression, then the argument is replaced with it's evaluated value.
```shell
$ py -m bulkexec echo "10 ** 5"
10000
```

If the evaluated value is an iterable (other than a string or bytes), the argument will be replaced with each element in the iterable one-by-one.
```shell
$ py -m bulkexec echo "range(5)"
0
1
2
3
4
```
If multiple arguments are iterables then commands will be launched by pairing the values element-wise. Shorter iterables cycle as to not exhaust their values.
```shell
$ py -m bulkexec echo "range(2)" "range(4)"
0 0
1 1
0 2
1 3
```
## Example Uses
Pinging multiple IP addresses:
```bash
py -m bulkexec ping "[f'192.168.1.{i}' for i in range(10)]" /n 1
```
<details>
    <summary>Example Output</summary>
    Pinging 192.168.1.0 with 32 bytes of data:
    Reply from 192.168.1.162: Destination host unreachable.

    Ping statistics for 192.168.1.0:
        Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),

    Pinging 192.168.1.1 with 32 bytes of data:
    Reply from 192.168.1.1: bytes=32 time=23ms TTL=64

    Ping statistics for 192.168.1.1:
        Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),
    Approximate round trip times in milli-seconds:
        Minimum = 23ms, Maximum = 23ms, Average = 23ms

    Pinging 192.168.1.2 with 32 bytes of data:
    Reply from 192.168.1.162: Destination host unreachable.

    Ping statistics for 192.168.1.2:
        Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),
</details>

## Special Cases
### Identical Argument Names
If a command argument shares the same name as a BulkExec argument it will by default be ignored. Only the last value of the argument will be used by BulkExec.
```bash
py -m bulkexec ping -h 
```
To pass this argument to the command instead, it can be wrapped in a combination of single and double quotes.
```bash
py -m bulkexec ping "'-h'"
py -m bulkexec ping '"-h"'
```