import re
import pandas as pd
import json

global_header_lines = 0

def read_license_file():
    # Reads the license data from its JSON-file and calls the extract_identifier-function.
    # Expects: None
    # Returns: A list of strings.
    with open("licenses.json", 'r') as file:
        data = json.load(file)
    license_list = extract_identifier(data['licenses'])
    return license_list


def extract_identifier(license_data):
    # Extracts the identifiers from the licenses and puts them in one list as strings.
    # Expects: A JSON-object containing the license data.
    # Returns: A list of strings.
    identifiers = []
    for license_identifier in license_data:
        identifiers.append(license_identifier['licenseId'])
    return identifiers


def read_csv(path):
    # Reads a csv-file into a pandas dataframe.
    # Expects: The path to the csv-file.
    # Returns: A pandas dataframe with the data from the csv-file.
    try:
        csv = pd.read_csv(path)
        return csv
    except FileNotFoundError:
        print("The file could not be found, please check the provided path!")


def remove_header_lines(header_lines, data_frame):
    # Removes additional header lines between the data-labels and the data.
    # Expects: - If only one header line an integer with the index of the line that is to be deleted or if multiple header
    #            lines a list-like with all indeces of the lines that are to be deleted. Example: '0' or '[0, 1]'
    #          - A reference to the dataframe the lines are to be deleted from.
    # Returns: No explicit return-value or object, the lines will be deleted from the referenced dataframe in place instead.
    global global_header_lines
    global_header_lines = len(header_lines)
    data_frame.drop(index=header_lines, inplace=True)


def fill_empyt_cells(data_frame):
    # Fills all empty cells in the dataframe with empty strings to prevent errors
    # Expects: A reference to a pandas dataframe.
    # Returns: No return-value or object, the cells will be filled in the referenced dataframe.
    data_frame.fillna("", inplace=True)


def check_authors(authors):
    # Checks the column 'Authors' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the authors strings.
    # Returns: A list of errors with line number and type of error.
    global global_header_lines
    author_errors = []
    for index, author in enumerate(authors):
        if author is "":
            author_errors.append(f"Line {index + global_header_lines + 2}: Mandatory attribute 'Author' is missing.")
            continue
        if '\*' in author:
            author_list = re.split("\s\*\s", author)
            for auth in author_list:
                if check_if_error(auth):
                    author_errors.append(f"Line {index + global_header_lines + 2}: Wrong name format.")
        else:
            if check_if_error(author):
                author_errors.append(f"Line {index + global_header_lines + 2}: Wrong name format.")
    return author_errors


def check_if_error(author):
    # Check the format of a name with a regular expression.
    # Expects: A string.
    # Returns: False if the string matches the constraints of the DIF and True if it doesnt.
    if re.search("^[A-Za-zäöüÄÖÜß]*,\s[A-Za-zäöüÄÖÜß]*$", author) is not None or re.search("[A-Za-zäöüÄÖÜß]*,\s[A-Za-zäöüÄÖÜß]*\s?:\s?\{\S*}$", author) is not None or re.search("^[A-Za-z0-9äöüÄÖÜß]*\s:\s\{organization", author) is not None or re.search("^n/a$", author) is not None:
        return False
    else:
        return True


def check_licenses(licenses):
    # Checks the column 'License' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the license strings.
    # Returns: A list of errors with line number and type of error.
    license_list = read_license_file()
    global global_header_lines
    license_errors = []

    for index, license_id in enumerate(licenses):
        if license_id is "":
            license_errors.append(f"Line {index + global_header_lines + 2}: License is missing.")
            continue
        if license_id not in license_list:
            license_errors.append(f"Line {index + global_header_lines + 2}: Provided License is not part of the list from 'https://spdx.org/licenses/' or is in a wrong format.")
    return license_errors


def check_link(link_list):
    # Checks the column 'Link' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the link strings.
    # Returns: A list of errors with line number and type of error.
    global global_header_lines
    link_errors = []

    for index, link in enumerate(link_list):
        if link is "":
            link_errors.append(f"Line {index + global_header_lines + 2}: Link is missing.")
            continue
        if re.search("^https://\S*$", link) is None:
            link_errors.append(f"Line {index + global_header_lines + 2}: Link is not in a valid format.")
    return link_errors

def check_title(titles):
    # Checks the column 'Title' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the title strings.
    # Returns: A list of errors with line number and type of error.
    global global_header_lines
    title_errors = []

    for index, title in enumerate(titles):
        if title is "":
            title_errors.append(f"Line {index + global_header_lines + 2}: Title is missing.")
    return title_errors


def check_data(dataframe):
    # Checks data within a dataframe according to the rules of the DIF.
    # Expects: A pandas dataframe.
    # Returns: A dictionary with the Attributes as keys and lists of all errors as values.
    found_errors = dict()

    if dataframe['Authors'] is not None:
        found_errors['Authors'] = check_authors(dataframe['Authors'])
    else:
        found_errors['Authors'] = "The mandatory Attribute 'Authors' is missing from every item!"

    if dataframe['License'] is not None:
        found_errors['License'] = check_licenses(dataframe['License'])
    else:
        found_errors['License'] = "The mandatory Attribute 'License' is missing from every item!"

    if dataframe['Link'] is not None:
        found_errors['Link'] = check_link(dataframe['Link'])
    else:
        found_errors['Link'] = "The mandatory Attribute 'License' is missing from every item!"

    if dataframe['Title'] is not None:
        found_errors['Title'] = check_title(dataframe['Title'])
    else:
        found_errors['Title'] = "The mandatory Attribute 'Title' is missing from every item!"

    return found_errors


if __name__ == '__main__':
    csv_file = read_csv("Courses_Register.csv")
    remove_header_lines([0], csv_file)
    fill_empyt_cells(csv_file)
    check_data(csv_file)