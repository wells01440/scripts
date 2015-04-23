#!/usr/bin/python
# -*- coding: utf8 -*-
"""
package.module
~~~~~~~~~~~~~
This module splits a text file into smaller text files. See the help in the command line parser text, below.
Blame Andy for stupid mistakes. Blame Ryan for the silly requirements
"""
import sys
import argparse
import os
import os.path
import logging


def main(args):
    """
    Main entry point.
    :param args: Command line args
    :return: Result code.
    """
    result = 0
    parser = argparse.ArgumentParser(
        description='Splits a text file into smaller files.',
        epilog='''Some important crap:
                  When you include a header record on each file, the line numbers
                  include that header record. Writing this thing would have been
                  a lot easier without that silly requirement.
                  Line delimiters are passed through Unix->Unix, Windows->Windows.
                  Avention PS...yeah, I like cheese. '''
    )
    parser.add_argument('-l', '--lines',
                        type=int,
                        dest='lines_per_file',
                        help='Number of lines per file',
                        # default=65565,
                        default=5,
                        required=False
                        )
    parser.add_argument('-c', '--copy-header',
                        dest='copy_header',
                        help='Copy header to output files (1st line in input file)',
                        action='store_true',
                        default=False,
                        required=False
                        )
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        help='Console diarrhea',
                        action='store_true',
                        default=False,
                        required=False
                        )
    parser.add_argument('-o', '--output_directory',
                        type=str,
                        dest='output_directory',
                        help='Destination directory.',
                        default='.',
                        required=False
                        )
    parser.add_argument('file_input_path',
                        help='Path to the file to be split',
                        )
    parsed = parser.parse_args()

    if parsed.verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
        logging.info("Verbose output.")
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")

    if os.path.exists(parsed.file_input_path):
        if os.path.isdir(parsed.output_directory):
            # these variables are predefined here to keep autopep from bitching
            out_file = None
            current_file = 0
            i = j = 0
            split_file_base_name = ''

            # fix stupid ../.././...whatever paths
            parsed.file_input_path = os.path.normpath(parsed.file_input_path)
            parsed.output_directory = os.path.normpath(parsed.output_directory)

            # get the prefix and extension ONLY from the basename
            input_file_prefix, input_file_extension = os.path.splitext(os.path.basename(parsed.file_input_path))

            # read the first line, save the header record
            with open(parsed.file_input_path, 'r') as f:
                header = f.readline()

            # Stupid challenge question which is why I'm still at work at 8:00 PM
            # --
            # Figure out how many zeros to pad estimated by size of file / length of the header / lines per file
            # line + 1 order of magnitude
            # (OK, it's cheating but I'd have to read the whole file, first which is wasteful.)
            # So instead I make the erroneous assumption that the header file will be the same as the rows.  I get
            # around this by adding one order of magnitude.  Maybe it'll work. If it doesn't, just statically
            # set the zfill width to something huge.
            file_size = os.path.getsize(parsed.file_input_path)
            record_size = len(header)
            zfill_width = len(str(round(file_size / record_size / parsed.lines_per_file))) + 1

            # Dump some debug
            logging.debug('Input file:       {0}'.format(parsed.file_input_path))
            logging.debug('Output Directory: {0}'.format(parsed.output_directory))
            logging.debug('Lines per file:   {0}'.format(parsed.lines_per_file))
            logging.debug('Copy header:      {0}'.format(parsed.copy_header))
            logging.debug('Zero_file width:  {0}'.format(zfill_width))

            with open(parsed.file_input_path, 'r') as input_file:
                for i, line in enumerate(input_file):
                    current_file = j // parsed.lines_per_file
                    if not j % parsed.lines_per_file:
                        split_file_base_name = '{prefix}_{number:0{width}d}{extension}'.format(
                            prefix=input_file_prefix,
                            number=current_file,
                            width=zfill_width,
                            extension=input_file_extension)
                        split_file_name = os.path.join(parsed.output_directory, split_file_base_name)
                        if out_file:
                            out_file.close()
                        if parsed.copy_header:
                            logging.debug('Writing {0} with 1 header row and {1} rows of data'.format(split_file_base_name, parsed.lines_per_file - 1))
                        else:
                            logging.debug('Writing {0} with {1} rows of data'.format(split_file_base_name, parsed.lines_per_file))
                        out_file = open(split_file_name, 'w')
                        if parsed.copy_header and current_file > 0:
                            j += 1
                            out_file.write(header)
                    if out_file:
                        j += 1
                        out_file.write('{}'.format(line))
                if out_file:
                    out_file.close()
                    if parsed.copy_header:
                        logging.debug('Writing {0} with 1 header row and {1} row(s) of data'.format(split_file_base_name, i % parsed.lines_per_file + 1))
                    else:
                        logging.debug('Writing {0} with {1} row(s) of data'.format(split_file_base_name, i % parsed.lines_per_file + 1))
                else:
                    logging.error('File I/O error')
                    result = 5
            print('Processing complete. Processed {} source records into {} file(s) '.format(i + 1, current_file + 1))
        else:
            logging.error('Invalid output directory. Output directory must exist and must be a directory. ')
            parser.print_help()
            result = 4
    else:
        logging.error('Invalid file. Input file does not exist. ')
        parser.print_help()
        result = 3
    return result


if __name__ == '__main__':
    sys.exit(main(sys.argv))
