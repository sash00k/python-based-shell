import io
import os
import sys
import re
from typing import TextIO
from pathlib import Path


def pwd(output: TextIO) -> None:
    print(os.getcwd(), file=output)


def cd(path: str, output: TextIO) -> None:
    new_path = Path(path).resolve()
    os.chdir(new_path)


def mkdir(path: str, output: TextIO) -> None:
    path_to_new_dir = Path(path).resolve()
    os.makedirs(path_to_new_dir)


def ls(args: list, output: TextIO) -> None:
    path_dir = Path(args[0]) if args else Path(os.getcwd())
    print(' '.join(sorted(map(str, os.listdir(path_dir)))), file=output)


def cat(args: list, output: TextIO, direction: str = 'forward') -> None:
    files_paths = map(lambda x: Path(x).resolve(), args)
    for file_path in files_paths:
        with open(file_path, 'r') as file:
            match direction:
                case 'forward':
                    result = file.readlines()
                case 'backwards':
                    result = file.readlines()[::-1]
            for cur_line in result:
                print(cur_line, end='', file=output)


def check_out_file(string: str, cur_out_stream: TextIO) -> (str, TextIO):
    if '>' in string:
        delimiter = string.find('>')
        command = string[:delimiter]
        cur_out_stream = open(Path(string.replace('>', '')[delimiter:].strip()).resolve(), 'a')
    else:
        command = string
    return command, cur_out_stream


def grep(args: list, output: TextIO) -> None:
    def grep_for_single_file(input_file: Path | str):
        suit_strings = []
        with open(input_file, 'r') as file:
            for cur_line in file.readlines():
                if re.findall(pattern, cur_line):
                    suit_strings.append(cur_line.strip('\n'))
            return suit_strings

    count_mode = False
    if '-c' in args:
        count_mode = True
        args.remove('-c')

    recursion_mode = False
    if '-r' in args:
        recursion_mode = True
        args.remove('-r')

    input_path = Path(args.pop()).resolve() if len(args) > 1 else False
    pattern = args.pop()[1:-1]

    result = ''
    # if recursion mode on (and not file's path given)
    if recursion_mode and not (input_path and input_path.is_file()):
        head_dir = input_path if input_path else Path(os.getcwd()).resolve()

        # recursively find all pairs (rel_path, file_path)
        files_paths = sorted([(os.path.join(path, filename).replace(os.getcwd(), '')[1:],
                               os.path.join(path, filename))
                              for path, dirs, filenames in os.walk(head_dir)
                              for filename in filenames])

        for rel_path, cur_file_path in files_paths:
            if count_mode:
                result += f'{rel_path}:{len(grep_for_single_file(cur_file_path))}\n'
            else:
                for suit_line in grep_for_single_file(rel_path):
                    result += f'{rel_path}:{suit_line}\n'

    # if recursion mode off (including case with '-r' and file were given)
    else:
        if count_mode:
            result += f'{len(grep_for_single_file(input_path))}\n'
        else:
            for suit_line in grep_for_single_file(input_path):
                result += f'{suit_line}\n'

    print(result, file=output, end='')


def solution(script: TextIO, output: TextIO) -> None:
    for cur_line in script.readlines():
        command, cur_output = check_out_file(string=cur_line, cur_out_stream=output)
        command = command.split()
        match command[0], command[1:]:
            case 'pwd', _:
                pwd(output=cur_output)
            case 'cd', args:
                cd(path=args[0], output=cur_output)
            case 'mkdir', args:
                mkdir(path=args[0], output=cur_output)
            case 'ls', args:
                ls(args=args, output=cur_output)
            case 'cat', args:
                cat(args=args, output=cur_output, direction='forward')
            case 'tac', args:
                cat(args=args, output=cur_output, direction='backwards')
            case 'grep', args:
                grep(args=args, output=cur_output)
            case _:
                print(f'unknown command "{command[0]}"', file=cur_output)


if __name__ == '__main__':
    print('$ ', end='')
    for line in sys.stdin:
        solution(io.StringIO(line), sys.stdout)
        print('$ ', end='')
