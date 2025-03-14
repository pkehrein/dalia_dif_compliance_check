import csv
import re

import pandas as pd
import json
from argparse import ArgumentParser

global_header_lines = 0
global_line_offset = 2
global_media_types = ["audio", "video", "text", "presentation", "code", "image", "multipart"]
global_proficiency_levels = ["novice", "advanced beginner", "competent", "proficient", "expert"]


def parse_arguments():
    parser = ArgumentParser(description="Check your csv-file if it is in compliance with the DALIA Interchange Format")
    parser.add_argument('input_filename')
    parser.add_argument('-o', '--output_filename',
                        help="Set the output filename to a custom value. Default is 'report'.")
    parser.add_argument('-l', '--header_lines', type=int,
                        help="If your csv-file contains more header lines than just the names of the columns, provide the number of lines to ensure accurate line errors.")

    return parser.parse_args()


def read_license_file():
    # Reads the license data from its JSON-file and calls the extract_identifier-function.
    # Expects: None.
    # Returns: A list of strings.
    with open("resources/licenses.json", 'r') as file:
        data = json.load(file)
    license_list = extract_identifier(data['licenses'])
    return license_list


def read_communities_list():
    # Reads the communities list from its JSON-file.
    # Expects: None.
    # Returns: A list of strings.
    with open("resources/communities.json", 'r') as file:
        data = json.load(file)
    return data


def read_data_formats_file():
    with open("resources/mimeData.json", 'r') as file:
        data = json.load(file)
    file_formats_list = extract_file_types(data)
    return file_formats_list


def extract_file_types(file_format_list):
    file_types = []
    for file_formats in file_format_list:
        file_format_types = file_formats["fileTypes"]
        for file_format in file_format_types:
            file_types.append(file_format)
    return file_types


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
        file = pd.read_csv(path)
        return file
    except FileNotFoundError:
        print("The file could not be found, please check the provided path!")


def remove_header_lines(header_lines, data_frame):
    # Removes additional header lines between the data-labels and the data.
    # Expects: - The number of header lines except the column names.
    #          - A reference to the dataframe the lines are to be deleted from.
    # Returns: No explicit return-value or object, the lines will be deleted from the referenced dataframe in place instead.
    global global_header_lines
    global_header_lines = header_lines
    for i in range(0, header_lines):
        data_frame.drop(index=i, inplace=True)


def fill_empty_cells(data_frame):
    # Fills all empty cells in the dataframe with empty strings to prevent errors
    # Expects: A reference to a pandas dataframe.
    # Returns: No return-value or object, the cells will be filled in the referenced dataframe.
    data_frame.fillna("", inplace=True)


def split_into_list(string):
    # Splits the given string at the delimiter '*' into list elements.
    # Expects: A string containing at least two items split by a '*'.
    # Returns: A list of strings.
    return re.split(r'\s\*\s', string)


def check_authors(authors):
    # Checks the column 'Authors' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the authors strings.
    # Returns: A list of errors with line number and type of error.
    author_errors = []
    for index, author in enumerate(authors):
        if author == "":
            author_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: Mandatory attribute 'Author' is missing.")
            continue
        if r'\*' in author:
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
    # Returns: False if the string matches the constraints of the DIF and True if it doesn't.
    if re.search(
            r"[\wäöüÄÖÜß-]+,\s[\wäöüÄÖÜß-]+(?:\s?:\s?\{\S*}|)+(?:$|\s\*\s[\wäöüÄÖÜß-]+,\s[\wäöüÄÖÜß-]+(?:\s?:\s?\{\S*}|)+)*",
            author) is not None or re.search(
        r"^[\S\s]*\s:\s\{organization", author) is not None or re.search("^n/a$", author) is not None:
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
        if license_id == "":
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
        if link == "":
            link_errors.append(f"Line {index + global_header_lines + global_line_offset}: Link is missing.")
            continue
        if re.search(r"^https://\S+(?:\s\*\shttps://\S+)*$", link) is None:
            link_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: Link is not in a valid format.")
    return link_errors


def check_title(titles):
    # Checks the column 'Title' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the title strings.
    # Returns: A list of errors with line number and type of error.
    title_errors = []

    for index, title in enumerate(titles):
        if title == "":
            title_errors.append(f"Line {index + global_header_lines + global_line_offset}: Title is missing.")
    return title_errors


def check_description(descriptions):
    # Checks the column 'Description' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing the description strings.
    # Returns: A list of errors with the line number and type of error.
    description_errors = []

    for index, description in enumerate(descriptions):
        if description == "":
            description_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide a description for a resource.")
    return description_errors


def check_community_format(string):
    # Checks the community string formatting.
    # Expects: A string.
    # Returns: If string is of format 'Community (S|R|RS)' False or no error and if not True or error found.
    if re.search(r'^[\S\s]*\s\((RS|SR|S|R)\)$', string) is not None:
        return False
    else:
        return True


def check_community_name(string):
    # Checks if the community name is in the list of community ids.
    # Expects: A string in the format 'Community ()'
    # Returns: True if in list, false if not.
    communities_list = read_communities_list()
    community_name = re.sub(r'\s\(\S*\)', '', string)
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
        if community == "":
            community_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide a Community, either as supporting or recommending entity.")
        else:
            if r"\*" in community:
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


def check_disciplines(disciplines):
    # Checks the column 'Discipline' according to the rules of the DIF.
    # Expects: A series from a pandas dataframe containing links to the relevant disciplines listed in https://skohub.io/dini-ag-kim/hochschulfaechersystematik/heads/master/w3id.org/kim/hochschulfaechersystematik/scheme.html
    # Returns: A list of errors with the line number and type of error.
    disciplines_errors = []

    for index, discipline in enumerate(disciplines):
        if discipline == "":
            disciplines_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide at least one relevant discipline as a link listed in https://skohub.io/dini-ag-kim/hochschulfaechersystematik/heads/master/w3id.org/kim/hochschulfaechersystematik/scheme.html .")
        else:
            if r"\*" in discipline:
                discipline_list = split_into_list(discipline)
                for disc in discipline_list:
                    disciplines_errors = check_single_discipline(disc, disciplines_errors, index)
            else:
                disciplines_errors = check_single_discipline(discipline, disciplines_errors, index)
    return disciplines_errors


def check_single_discipline(discipline, discipline_errors, index):
    if check_discipline_link(discipline):
        discipline_errors.append(
            f"Line {index + global_header_lines + global_line_offset}: The provided format is not of the type xsd:anyURI.")

    return discipline_errors


def check_discipline_link(discipline):
    if re.search(r"^https://w3id\.org/kim/hochschulfaechersystematik/n\d+", discipline) is not None:
        return False
    else:
        return True


def check_media_types(mediatypes):
    media_type_errors = []

    for index, media_type in enumerate(mediatypes):
        if media_type == "":
            media_type_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide a media type for learning resources")
        else:
            if '*' in media_type:
                type_list = split_into_list(media_type)
                for element in type_list:
                    if element not in global_media_types:
                        media_type_errors.append(
                            f"Line {index + global_header_lines + global_line_offset}: The provided media type is not in the DIF picklist.")
            else:
                if media_type not in global_media_types:
                    media_type_errors.append(
                        f"Line {index + global_header_lines + global_line_offset}: The provided media type is not in the DIF picklist.")
    return media_type_errors


def check_proficiency_levels(proficiency_levels):
    proficiency_level_errors = []

    for index, proficiency_level in enumerate(proficiency_levels):
        if proficiency_level == "":
            proficiency_level_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide at least one proficiency level for learning resources.")
        else:
            if '*' in proficiency_level:
                level_list = split_into_list(proficiency_level)
                for level in level_list:
                    if level not in global_proficiency_levels:
                        proficiency_level_errors.append(
                            f"Line {index + global_header_lines + global_line_offset}: The provided proficiency level is not in the DIF picklist.")
            else:
                if proficiency_level not in global_proficiency_levels:
                    proficiency_level_errors.append(
                        f"Line {index + global_header_lines + global_line_offset}: The provided proficiency level is not in the DIF picklist.")
    return proficiency_level_errors


def check_date_format(publication_date):
    if re.search(r"^\d{4}-\d{2}-\d{2}$", publication_date) is None and re.search(r"^\d{4}-\d{2}$",
                                                                                publication_date) is None and re.search(
            r"^\d{4}$", publication_date) is None:
        return True
    else:
        return False


def check_publication_dates(publication_dates):
    publication_date_errors = []

    for index, publication_date in enumerate(publication_dates):
        if publication_date == "":
            publication_date_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide a publication date for learning resources.")
        else:
            if check_date_format(publication_date):
                publication_date_errors.append(
                    f"Line {index + global_header_lines + global_line_offset}: The provided publication date is not of the format xsd:date."
                )

    return publication_date_errors


def check_file_format(file_formats):
    file_formats_list = read_data_formats_file()
    file_format_errors = []

    for index, file_format in enumerate(file_formats):
        if file_format == "":
            file_format_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide the file format of a learning resource.")
        else:
            if check_file_format_format(file_format):
                file_format_errors.append(
                    f"Line {index + global_header_lines + global_line_offset}: The provided file format is not formatted properly.")
            else:
                file_format_list = split_into_list(file_format)
                if check_file_format_list(file_format_list, file_formats_list):
                    file_format_errors.append(
                        f"Line {index + global_header_lines + global_line_offset}: The provided file format is not included in the picklist.")

    return file_format_errors


def check_file_format_format(file_format):
    if re.search(r"^\.\w+(?:$|\s\*\s\.\w+)*$", file_format) is None:
        return True
    else:
        return False


def check_file_format_list(file_format_list, file_formats):
    for file_format in file_format_list:
        if file_format not in file_formats:
            return True
    return False


def check_target_group(target_groups):
    target_groups_list = read_csv("resources/target_audience.csv")
    target_group_errors = []

    for index, target_group in enumerate(target_groups):
        if target_group == "":
            target_group_errors.append(
                f"Line {index + global_header_lines + global_line_offset}: It is recommended to provide at least one target group for a learning resource.")
        else:
            if check_target_group_format(target_group):
                target_group_errors.append(
                    f"Line {index + global_header_lines + global_line_offset}: The provided target groups are not formatted properly.")
            else:
                target_group_list = split_into_list(target_group)
                if check_target_group_list(target_group_list, target_groups_list):
                    target_group_errors.append(
                        f"Line {index + global_header_lines + global_line_offset}: The provided target group is not included in the picklist.")
    return target_group_errors


def check_target_group_format(target_group):
    if re.search(r"^\w+(?:\s\(?\w+\)?)?(?:$|\s\*\s\w+(?:$|\s\(?\w+\)?))*", target_group) is None:
        return True
    else:
        return False


def check_target_group_list(target_group_list, target_groups):
    for target_group in target_group_list:
        if target_group not in target_groups:
            return True
    return False


def check_data(dataframe):
    # Checks data within a dataframe according to the rules of the DIF.
    # Expects: A pandas dataframe.
    # Returns: A dictionary with the Attributes as keys and lists of all errors as values.
    errors = dict()

    if dataframe['Authors'] is not None:
        errors['Authors'] = check_authors(dataframe['Authors'])
    else:
        errors['Authors'] = "The mandatory Attribute 'Authors' is missing from every item!"

    if dataframe['License'] is not None:
        errors['License'] = check_licenses(dataframe['License'])
    else:
        errors['License'] = "The mandatory Attribute 'License' is missing from every item!"

    if dataframe['Link'] is not None:
        errors['Link'] = check_link(dataframe['Link'])
    else:
        errors['Link'] = "The mandatory Attribute 'License' is missing from every item!"

    if dataframe['Title'] is not None:
        errors['Title'] = check_title(dataframe['Title'])
    else:
        errors['Title'] = "The mandatory Attribute 'Title' is missing from every item!"

    if dataframe['Description'] is not None:
        errors['Description'] = check_description(dataframe['Description'])
    else:
        errors['Description'] = "It is recommended to provide a description for every item!"

    if dataframe['Community'] is not None:
        errors['Community'] = check_community(dataframe['Community'])
    else:
        errors[
            'Community'] = "It is recommended to provide information about recommending and supporting communities!"

    if dataframe['Discipline'] is not None:
        errors['Discipline'] = check_disciplines(dataframe['Discipline'])
    else:
        errors[
            'Discipline'] = "It is recommended to provide at least one relevant discipline listed in https://skohub.io/dini-ag-kim/hochschulfaechersystematik/heads/master/w3id.org/kim/hochschulfaechersystematik/scheme.html"

    if dataframe['MediaType'] is not None:
        errors['MediaType'] = check_media_types(dataframe['MediaType'])
    else:
        errors['MediaType'] = "It is recommended to provide media types for learning resources."

    if dataframe['ProficiencyLevel'] is not None:
        errors['ProficiencyLevel'] = check_proficiency_levels(dataframe['ProficiencyLevel'])
    else:
        errors['ProficiencyLevel'] = "It is recommended to provide proficiency levels for learning resources."

    if dataframe['PublicationDate'] is not None:
        errors['PublicationDate'] = check_publication_dates(dataframe['PublicationDate'])
    else:
        errors['PublicationDate'] = "It is recommended to provide publication dates for learning resources."

    if dataframe['FileFormat'] is not None:
        errors['FileFormat'] = check_file_format(dataframe['FileFormat'])
    else:
        errors['FileFormat'] = "It is recommended to provide the file formats of the resources."

    if dataframe['TargetGroup'] is not None:
        errors['TargetGroup'] = check_target_group(dataframe['TargetGroup'])
    else:
        errors['TargetGroup'] = "It is recommended to provide at least one target group for a learning resource."

    return errors


def write_output(errors, file_name):
    fieldnames = errors.keys()
    max_length = max(len(values) for values in errors.values())
    with open(file_name, 'w', newline="") as report:
        writer = csv.writer(report)
        writer.writerow(fieldnames)

        for i in range(max_length):
            row = []
            for key in errors:
                if i < len(errors[key]):
                    row.append(errors[key][i])
                else:
                    row.append('')
            writer.writerow(row)


if __name__ == '__main__':
    args = parse_arguments()

    csv_file = read_csv(args.input_filename)
    if args.header_lines is not None and args.header_lines > 0:
        remove_header_lines(args.header_lines, csv_file)
    fill_empty_cells(csv_file)
    found_errors = check_data(csv_file)

    if args.output_filename is not None:
        filename = f"./{args.output_filename}.csv"
    else:
        filename = f"./report-{args.input_filename}.csv"
    write_output(found_errors, filename)
