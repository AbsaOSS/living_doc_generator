"""Convert Features to Pages

This script is used to convert consolidated feature data into individual markdown files.
It reads a JSON file containing consolidated feature data, processes this data, and generates
 a markdown file for each feature.

 The script can be run from the command line with optional arguments:
    * python3 convert_features_to_pages.py
 """

import json
import os
import re
from datetime import datetime
from utils import ensure_folder_exists, parse_arguments
from typing import Dict, List, Any

INPUT_FILE = "../data/feature_consolidation/feature.consolidation.json"
PAGE_TEMPLATE_FILE = "../templates/page_feature_template.md"
INDEX_PAGE_TEMPLATE_FILE = "../templates/_index_feature_template.md"
OUTPUT_DIRECTORY_ROOT = "../output/liv-doc"
OUTPUT_DIRECTORY_FEATURE = "features"
OUTPUT_DIRECTORY = os.path.join(OUTPUT_DIRECTORY_ROOT, OUTPUT_DIRECTORY_FEATURE)
MISSING_VALUE_SYMBOL = "---"
NOT_MINED_SYMBOL = "-?-"


def replace_template_placeholders(template: str, replacement: Dict[str, str]) -> str:
    """
        Replaces placeholders in a template ({replacement}) with corresponding values from a dictionary.

        @param template: The string template containing placeholders.
        @param replacement: The dictionary containing keys and values for replacing placeholders.

        @return: The updated template string with replaced placeholders.
    """

    # Update template with values from replacement dictionary
    for key, value in replacement.items():
        if value is not None:
            template = template.replace(f"{{{key}}}", value)
        else:
            template = template.replace(f"{{{key}}}", MISSING_VALUE_SYMBOL)

    return template


def generate_feature_info(feature: Dict[str, Any]) -> str:
    """
        Generates a string representation of feature info in a table format.

        @param feature: The dictionary containing feature data.

        @return: A string representing the feature information in a table format.
    """

    # Get the feature labels and join them into one string
    labels = feature.get('Labels', [])
    labels = ', '.join(labels) if labels else MISSING_VALUE_SYMBOL

    # Define the headers for every row in the table
    headers = ["Owner",
               "Repository name",
               "Feature number",
               "State",
               "Labels",
               "URL",
               "Created at",
               "Updated at",
               "Closed at",
               "Milestone number",
               "Milestone title",
               "Milestone HTML URL"]

    # Define the values adequate to the headers
    values = [
        feature.get('Owner', MISSING_VALUE_SYMBOL),
        feature.get('RepositoryName', MISSING_VALUE_SYMBOL),
        feature.get('Number', MISSING_VALUE_SYMBOL),
        feature.get('State', MISSING_VALUE_SYMBOL).lower(),
        labels,
        feature.get('URL', MISSING_VALUE_SYMBOL),
        feature.get('CreatedAt', MISSING_VALUE_SYMBOL),
        feature.get('UpdatedAt', MISSING_VALUE_SYMBOL),
        feature.get('ClosedAt', MISSING_VALUE_SYMBOL),
        feature.get('MilestoneNumber', MISSING_VALUE_SYMBOL),
        feature.get('MilestoneTitle', MISSING_VALUE_SYMBOL),
        feature.get('MilestoneHtmlUrl', MISSING_VALUE_SYMBOL)
    ]

    # Initialize the feature_info string with the table header
    feature_info = f"| Attribute | Content |\n|---|---|\n"

    # Add all attributes to the feature information table
    for attribute, content in zip(headers, values):
        feature_info += f"| {attribute} | {content} |\n"

    return feature_info


def generate_project_info(feature: Dict[str, Any], feature_table: str) -> str:
    """
        Adds project-related information to the feature info table.

        @param feature: The dictionary containing feature data.
        @param feature_table: The table string containing the feature information.

        @return: The updated feature information table with added project-related information.
    """

    project_title = feature.get('ProjectTitle', MISSING_VALUE_SYMBOL)

    # Define headers for project rows
    headers = [
        "Project title",
        "Status",
        "Priority",
        "Size",
        "MoSCoW"
    ]

    # If project mining is not allowed, set values to not mined symbol
    if project_title == 'Not mined':
        values = [NOT_MINED_SYMBOL] * len(headers)

    # If feature has no project attached, add info about no project
    elif project_title == MISSING_VALUE_SYMBOL:
        values = [MISSING_VALUE_SYMBOL] * len(headers)

    else:
        values = [
            project_title,
            feature.get('Status', MISSING_VALUE_SYMBOL),
            feature.get('Priority', MISSING_VALUE_SYMBOL),
            feature.get('Size', MISSING_VALUE_SYMBOL),
            feature.get('MSCW', MISSING_VALUE_SYMBOL)
        ]

    # Update the feature table with project info
    for attribute, content in zip(headers, values):
        feature_table += f"| {attribute} | {content} |\n"

    return feature_table


def generate_md_feature_file(page_template: str, feature: Dict[str, Any], output_directory: str) -> None:
    """
        Generates a markdown file for a given feature using a specified template.

        @param page_template: The string template for the single page markdown file.
        @param feature: The dictionary containing feature data.
        @param output_directory: The directory where the markdown file will be saved.

        @return: None
    """

    # Initialize all replacements for generating page from a template
    page_title = feature.get("Title", "Title not defined")
    feature_table = generate_feature_info(feature)
    feature_info = generate_project_info(feature, feature_table)
    date = datetime.now().strftime("%Y-%m-%d")
    content = feature.get("Body", "Feature has no content")

    # Initialize dict with template parts
    replacements = {
        "title": page_title,
        "date": date,
        "page_heading": page_title,
        "feature_info": feature_info,
        "body": content
    }

    # Run through all replacements and update template with adequate content
    feature_md_page = replace_template_placeholders(page_template, replacements)

    page_name = feature["PageFilename"]

    # Save the feature markdown page
    with open(os.path.join(output_directory, page_name), 'w', encoding='utf-8') as feature_file:
        feature_file.write(feature_md_page)

    print(f"Generated {page_name}.")


def generate_feature_line(feature: Dict[str, Any]) -> str:
    """
        Generates a markdown summary line for a given feature.

        @param feature: The dictionary containing feature data.

        @return: A string representing the markdown line for the feature.
    """

    # Extract feature details from the feature dict
    owner = feature.get('Owner', MISSING_VALUE_SYMBOL)
    repo_name = feature.get('RepositoryName', MISSING_VALUE_SYMBOL)
    number = feature.get('Number', MISSING_VALUE_SYMBOL)
    title = feature.get('Title', MISSING_VALUE_SYMBOL)
    title = title.replace("|", " _ ")
    url = feature.get('URL', MISSING_VALUE_SYMBOL)
    md_filename = feature.get('PageFilename', MISSING_VALUE_SYMBOL)
    project_title = feature.get('ProjectTitle', MISSING_VALUE_SYMBOL)

    status = NOT_MINED_SYMBOL if project_title == 'Not mined' else feature.get('Status', MISSING_VALUE_SYMBOL)

    md_feature_line = f"|{owner} | {repo_name} | [#{number} - {title}]({md_filename}) | {status} |[GitHub]({url}) |"

    return md_feature_line


def group_features_by_milestone(features: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
        Groups features by their milestone.

        @param features: A list of all consolidated features.

        @return: A dictionary where each key is a milestone title and the value is a list of features
         under that milestone.
    """

    # Initialize a dict to store all milestones
    milestones = {}

    for feature in features:
        milestone_title = f"{feature['MilestoneTitle']}"

        # Create a milestone structure if it does not exist
        if milestone_title not in milestones:
            milestones[milestone_title] = []

        # Add the feature to the correct milestone
        milestones[milestone_title].append(feature)

    return milestones


def generate_milestone_block(milestone_table_header: str, milestone_title: str, feature_lines: List[str]) -> str:
    """
        Generates a markdown block for a given milestone and its features.

        @param milestone_table_header: The table header for the milestone block.
        @param milestone_title: The title of the milestone.
        @param feature_lines: A list of markdown lines, each representing a feature.

        @return: A string representing the markdown block for the milestone.
    """

    # Combine the milestone title, table header, and feature lines into a markdown block
    milestone_block = f"\n### {milestone_title}\n" + milestone_table_header + "\n".join(feature_lines)

    return milestone_block


def process_features(milestones: Dict[str, List[Dict[str, Any]]],
                     template_feature_page: str,
                     milestonesAsChapters: bool) -> str:
    """
        Processes features and generates a markdown file for each feature.

        @param milestones: A dictionary where each key is a milestone title and the value is a list of features under that milestone.
        @param template_feature_page: The string template for the single page markdown file.
        @param milestonesAsChapters: A boolean switch indicating whether milestones should be treated as chapters.

        @return: A string containing all the generated markdown blocks for the processed features.
    """

    features = ""
    milestone_table_header = """| Owner      | Repository name | Feature 'Number - Title'  | Status  |URL   |
           |------------------------------|-----------------|---------------------------|---------|------|
           """

    # If milestones are not treated as chapters, add table header
    if not milestonesAsChapters:
        features += "\n" + milestone_table_header

    for milestone_title, feature_list in sorted(milestones.items()):
        # Generate milestone block for all features
        feature_lines = [generate_feature_line(feature) for feature in feature_list]

        # Generate tables based on using milestones as chapters
        if milestonesAsChapters:
            features += generate_milestone_block(milestone_table_header, milestone_title, feature_lines)
        else:
            features += "\n".join(feature_lines)

        # Generate markdown file for every feature
        for feature in feature_list:
            generate_md_feature_file(template_feature_page, feature, OUTPUT_DIRECTORY)

    return features


def generate_table_of_contents(content: str) -> str:
    """
    Generates a table of contents for a given markdown content.

    @param content: The string containing the markdown content.

    @return: A string representing the table of contents in a md format.
    """

    # Find all headings in the content
    headings = re.findall(r"(#+) (.+)", content)

    # Set the table of contents
    toc = []

    # Add the table of contents header
    toc.append("## Table of Contents")

    for level, title in headings:
        # Ignore Heading 1
        if len(level) == 1:
            continue

        # Normalize the title to create anchor links
        normalized_title = re.sub(r"[^\w\s-]", '', title.lower())
        anchor_link = normalized_title.replace(' ', '-')

        # Calculate the indentation based on number of hash marks
        indentation = ' ' * 4 * (len(level) - 2)

        # Create md string for the table of contents
        toc_link = f"{indentation}- [{title}](#{anchor_link})"

        toc.append(toc_link)

    # ToC into single string separated
    toc_string = "\n".join(toc)

    return toc_string


def generate_index_page(features: str, template_index_page: str, milestonesAsChapters: bool) -> None:
    """
        Generates an index summary markdown page for all features.

        @param features: A string containing all the generated markdown blocks for the features.
        @param template_index_page: The string template for the index markdown page.
        @param milestonesAsChapters: A boolean switch indicating whether milestones should be treated as chapters.

        @return: None
    """

    # Prepare feature dict for replacing placeholders
    feature_replacement = {
        "features": features
    }

    # Replace the feature placeholders
    index_page_content = replace_template_placeholders(template_index_page, feature_replacement)

    # Generate table of contents, if content is divided into milestones
    table_of_contents = generate_table_of_contents(index_page_content) if milestonesAsChapters else ""

    # Prepare additional replacements for the index page
    replacements = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "table-of-contents": table_of_contents
    }

    # Second wave of replacing placeholders
    index_page = replace_template_placeholders(index_page_content, replacements)

    # Create an index page file
    with open(os.path.join(OUTPUT_DIRECTORY, "_index.md"), 'w', encoding='utf-8') as index_file:
        index_file.write(index_page)

    print("Generated _index.md.")


if __name__ == "__main__":
    # Get environment variables set by the controller script
    user_token = os.getenv('GITHUB_TOKEN')
    milestones_as_chapters = os.getenv('MILESTONES_AS_CHAPTERS')

    # Parse the boolean values
    milestones_as_chapters = milestones_as_chapters.lower() == 'true'

    print("Environment variables:")
    print(f"MILESTONES_AS_CHAPTERS: {milestones_as_chapters}")

    # Get the current directory and ensure the output directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(os.path.join(current_dir, OUTPUT_DIRECTORY), current_dir)

    print("Starting the feature page generation process.")

    # Load consolidated feature data
    with open(INPUT_FILE, 'r', encoding='utf-8') as json_file:
        features_data = json.load(json_file)

    # Load page template
    with open(PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as template_file:
        template_feature_page = template_file.read()

    # Load index page template
    with open(INDEX_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as idx_page_template_file:
        template_index_page = idx_page_template_file.read()

    # Organize feature data by milestones and state
    milestones = group_features_by_milestone(features_data)

    # Process features and generate md pages
    features = process_features(milestones, template_feature_page, milestones_as_chapters)

    # Generate index page
    generate_index_page(features, template_index_page, milestones_as_chapters)

    print(f"Living documentation generated on the path: {os.path.join(current_dir, OUTPUT_DIRECTORY_ROOT)}")
