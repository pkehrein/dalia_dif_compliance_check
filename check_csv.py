import re
import pandas as pd
import json

global_header_lines = 0
global_line_offset = 2


def read_license_file():
    # Reads the license data from its JSON-file and calls the extract_identifier-function.
    # Expects: None.
    # Returns: A list of strings.
    with open("licenses.json", 'r') as file:
        data = json.load(file)
    license_list = extract_identifier(data['licenses'])
    return license_list


def read_communities_list():
    # Reads the communities list from its JSON-file.
    # Expects: None.
    # Returns: A list of strings.
    with open("communities.json", 'r') as file:
        data = json.load(file)
    return data


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


def split_into_list(string):
    # Splits the given string at the delimiter '*' into list elements.
    # Expects: A string containing at least two items split by a '*'.
    # Returns: A list of strings.
    return re.split("\s\*\s", string)


def check_authors(authors):
    # Checks the column 'Authors' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the authors strings.
    # Returns: A list of errors with line number and type of error.
    author_errors = []
    for index, author in enumerate(authors):
        if author is "":
            author_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: Mandatory attribute 'Author' is missing.")
            continue
        if '\*' in author:
            author_list = split_into_list(author)
            for auth in author_list:
                if check_author_format(auth):
                    author_errors.append(f"Line {index + global_header_lines + global_line_offset}: Wrong name format.")
        else:
            if check_author_format(author):
                author_errors.append(f"Line {index + global_header_lines + global_line_offset}: Wrong name format.")
    return author_errors


def check_author_format(author):
    # Check the format of a name with a regular expression.
    # Expects: A string.
    # Returns: False if the string matches the constraints of the DIF and True if it doesnt.
    if re.search("^[A-Za-zäöüÄÖÜß]*,\s[A-Za-zäöüÄÖÜß]*$", author) is not None or re.search(
            "[A-Za-zäöüÄÖÜß]*,\s[A-Za-zäöüÄÖÜß]*\s?:\s?\{\S*}$", author) is not None or re.search(
            "^[A-Za-z0-9äöüÄÖÜß]*\s:\s\{organization", author) is not None or re.search("^n/a$", author) is not None:
        return False
    else:
        return True


def check_licenses(licenses):
    # Checks the column 'License' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the license strings.
    # Returns: A list of errors with line number and type of error.
    license_list = read_license_file()
    license_errors = []

    for index, license_id in enumerate(licenses):
        if license_id is "":
            license_errors.append(f"Line {index + global_header_lines + global_line_offset}: License is missing.")
            continue
        if license_id not in license_list:
            license_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: Provided License is not part of the list from 'https://spdx.org/licenses/' or is in a wrong format.")
    return license_errors


def check_link(link_list):
    # Checks the column 'Link' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the link strings.
    # Returns: A list of errors with line number and type of error.
    global global_header_lines
    link_errors = []

    for index, link in enumerate(link_list):
        if link is "":
            link_errors.append(f"Line {index + global_header_lines + global_line_offset}: Link is missing.")
            continue
        if re.search("^https://\S*$", link) is None:
            link_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: Link is not in a valid format.")
    return link_errors


def check_title(titles):
    # Checks the column 'Title' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the title strings.
    # Returns: A list of errors with line number and type of error.
    title_errors = []

    for index, title in enumerate(titles):
        if title is "":
            title_errors.append(f"Line {index + global_header_lines + global_line_offset}: Title is missing.")
    return title_errors


def check_description(descriptions):
    # Checks the column 'Description' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the description strings.
    # Returns: A list of errors with the line number and type of error.
    description_errors = []

    for index, description in enumerate(descriptions):
        if description is "":
            description_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide a description for a resource.")
    return description_errors


def check_community_format(string):
    # Checks the community string formatting.
    # Expects: A string.
    # Returns: If string is of format 'Community (S|R|RS) False or no error and if not True or error found.
    if re.search('^[A-Za-z0-9äöüÄÖÜß]*\s\((RS|SR|S|R)\)$', string) is not None:
        return False
    else:
        return True


def check_community_name(string):
    # Checks if the community name is in the list of community ids.
    # Expects: A string in the format 'Community ()'
    # Returns: True if in list, false if not.
    communities_list = read_communities_list()
    community_name = re.sub('\s\(\S*\)', '', string)
    if community_name in communities_list["subsidiaries"]:
        return True
    else:
        return False


def check_community(communities):
    # Checks the column 'Community' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the supporting or recommending communities.
    # Returns: A list of errors with the line number and type of error.
    community_errors = []

    for index, community in enumerate(communities):
        if community is "":
            community_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide a Community, either as supporting or recommending entity.")
        else:
            if "\*" in community:
                community_list = split_into_list(community)
                for com in community_list:
                    community_errors = check_single_community(com, community_errors, index)
            else:
                community_errors = check_single_community(community, community_errors, index)
    return community_errors


def check_single_community(com, community_errors, index):
    if check_community_format(com):
        community_errors.append(
            f"Line {index + global_header_lines + global_line_offset}: The provided format for the community contains errors.")
    if not check_community_name(com):
        community_errors.append(
            f"Line {index + global_header_lines + global_line_offset}: The provided name does not match any name from the subsidiaries list. Please check if the name is correct. If it is you can ignore this warning.")
    return community_errors


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

    if dataframe['Description'] is not None:
        found_errors['Description'] = check_description(dataframe['Description'])
    else:
        found_errors['Description'] = "It is recommended to provide a description for every item!"

    if dataframe['Community'] is not None:
        found_errors['Community'] = check_community(dataframe['Community'])
    else:
        found_errors[
            'Community'] = "It is recommended to provide information about recommending and supporting commnities!"

    return found_errors


if __name__ == '__main__':
    csv_file = read_csv("Courses_Register.csv")
    remove_header_lines([0], csv_file)
    fill_empyt_cells(csv_file)
    check_data(csv_file)
