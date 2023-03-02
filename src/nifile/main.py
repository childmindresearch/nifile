import argparse

from .nifile import probe_file


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=str, help='Path to (neuro-imaging) file.')
    parser.add_argument('-o', '--output', type=str, help='(Optional) path to output json file (will print to console '
                                                         'if none given).')
    parser.add_argument('-d', '--deep', action='store_true', help='Analyze the file and collect additional meta '
                                                                       'information.')

    args = parser.parse_args()

    probe_file(
        path_input=args.input,
        path_output=args.output,
        deep=args.deep
    )


if __name__ == '__main__':
    main()