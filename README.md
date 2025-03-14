# DALIA Interchange Format Compliance Check  

## Description  

This repository includes a Python script to check the compliance of CSV-files with the [DALIA Interchange Format](https://zenodo.org/records/11521029).

## Requirements  

- [Python 3.x](https://www.python.org/downloads/)
- pandas package
- json package

## Installation

Clone the repository or download the check_csv.py file and the resources directory. Ensure Python 3.x is installed and install the required libraries using:

``pip install pandas json``

## Usage

Run the script with the following command:

``python3 check_csv.py [INPUTFILE_NAME] -o [OUTPUTFILE_NAME] -l [NUMBER_OF_HEADER_LINES]``

Example:

``python3 check_csv.py input.csv -o output -l 2``

Flags:

* -o: Name of the generated output csv-file. Default: [INPUTFILE_NAME]-report
* -l: Number of header lines excluding the headings/names of columns. It is not required but recommended to input the number of lines as to not generate unnecessary errors. Default: 0

You can also use:

``python3 check_csv.py --help``

To get an overview over all flags listed above in your terminal.

## Output

The script outputs a csv-file containing all errors and recommendations found in the input-csv-file. The errors will be sorted by the categories of the DALIA Interchange Format.

## Contributors

@author: Paul Kehrein [https://orcid.org/0009-0004-6540-6498](https://orcid.org/0009-0004-6540-6498)

Further contributors are very welcome!

## License

All code covered by the [MIT](https://opensource.org/license/MIT) license.