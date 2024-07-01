"""Convert Features to Pages

This script is used to convert consolidated feature data into individual markdown files.
It reads a JSON file containing consolidated feature data, processes this data, and generates
 a markdown file for each feature.

 The script can be run from the command line with optional arguments:
    * python3 convert_issues_to_pages.py
 """

import json
import os
import re
from datetime import datetime
from typing import Dict, List

from utils import ensure_folder_exists
from containers.consolidated_issue import ConsolidatedIssue

CONSOLIDATION_FILE = "../data/issue_consolidation/issue.consolidation.json"
ISSUE_PAGE_TEMPLATE_FILE = "../templates/issue_page_template.md"
INDEX_PAGE_TEMPLATE_FILE = "../templates/_index_page_template.md"
OUTPUT_DIRECTORY_ROOT = "../output/liv-doc"
OUTPUT_DIRECTORY_ISSUE = "issues"
OUTPUT_DIRECTORY = os.path.join(OUTPUT_DIRECTORY_ROOT, OUTPUT_DIRECTORY_ISSUE)


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
            template = template.replace(f"{{{key}}}", "")

    return template


def generate_issue_summary_table(consolidated_issue: ConsolidatedIssue) -> str:
    """
        Generates a string representation of feature info in a table format.

        @param consolidated_issue: The dictionary containing feature data.

        @return: A string representing the feature information in a table format.
    """
    # Get the issue labels and join them into one string
    labels = consolidated_issue.labels
    # TODO: not sure with this one
    labels = ', '.join(labels) if labels else None

    # Get the issue URL and format it as a Markdown link
    issue_url = consolidated_issue.url
    issue_url = f"[GitHub link]({issue_url})" if issue_url else None

    # Define the header for the issue summary table
    # TODO: How to work with error in consolidated_issue.error
    headers = [
        "Organization name",
        "Repository name",
        "Issue number",
        "State",
        "Issue URL",
        "Created at",
        "Updated at",
        "Closed at",
        "Labels"
        ]

    # Define the values for the issue summary table
    values = [
        consolidated_issue.organization_name,
        consolidated_issue.repository_name,
        consolidated_issue.number,
        consolidated_issue.state.lower(),
        issue_url,
        consolidated_issue.created_at,
        consolidated_issue.updated_at,
        consolidated_issue.closed_at,
        labels
    ]

    # Update the summary table, if issue has a milestone object
    if consolidated_issue.milestone is not None:
        milestone_url = consolidated_issue.milestone.html_url
        milestone_url = f"[GitHub link]({milestone_url})"

        headers.extend([
            "Milestone number",
            "Milestone title",
            "Milestone URL"
        ])

        values.extend([
            consolidated_issue.milestone.number,
            consolidated_issue.milestone.title,
            milestone_url
        ])
    else:
        headers.append("Milestone")
        values.append(None)

    # Update the summary table, if issue is linked to the project
    if consolidated_issue.linked_to_project:
        headers.extend([
            "Project title",
            "Status",
            "Priority",
            "Size",
            "MoSCoW"
        ])

        values.extend([
            consolidated_issue.project_title,
            consolidated_issue.status,
            consolidated_issue.priority,
            consolidated_issue.size,
            consolidated_issue.moscow
        ])
    else:
        headers.append("Linked to project")
        values.append(consolidated_issue.linked_to_project)

    # Initialize the Markdown table
    issue_info = f"| Attribute | Content |\n|---|---|\n"

    # Add together all the attributes from the summary table in Markdown format
    for attribute, content in zip(headers, values):
        issue_info += f"| {attribute} | {content} |\n"

    return issue_info


def generate_md_issue_page(issue_page_template: str, consolidated_issue: ConsolidatedIssue, output_directory: str) -> None:
    """
        Generates a markdown file for a given feature using a specified template.

        @param issue_page_template: The string template for the single page markdown file.
        @param consolidated_issue: The dictionary containing feature data.
        @param output_directory: The directory where the markdown file will be saved.

        @return: None
    """

    # Get all replacements for generating single issue page from a template
    title = consolidated_issue.title
    date = datetime.now().strftime("%Y-%m-%d")
    issue_content = consolidated_issue.body

    # Generate a summary table for the issue
    issue_table = generate_issue_summary_table(consolidated_issue)

    # Initialize dictionary with replacements
    replacements = {
        "title": title,
        "date": date,
        "page_issue_title": title,
        "issue_summary_table": issue_table,
        "issue_content": issue_content
    }

    # Run through all replacements and update template keys with adequate content
    issue_md_page = replace_template_placeholders(issue_page_template, replacements)

    # Get the page filename for naming single issue output correctly
    page_filename = consolidated_issue.page_filename

    # Save the single issue Markdown page
    with open(os.path.join(output_directory, page_filename), 'w', encoding='utf-8') as issue_file:
        issue_file.write(issue_md_page)

    print(f"Generated {page_filename}.")


def generate_issue_line(consolidated_issue: ConsolidatedIssue) -> str:
    """
        Generates a markdown summary line for a given feature.

        @param consolidated_issue: The dictionary containing feature data.

        @return: A string representing the markdown line for the feature.
    """

    # Extract issue details from the consolidated issue object
    organization_name = consolidated_issue.organization_name
    repository_name = consolidated_issue.repository_name
    number = consolidated_issue.number
    title = consolidated_issue.title
    title = title.replace("|", " _ ")
    page_filename = consolidated_issue.page_filename
    status = consolidated_issue.status
    url = consolidated_issue.url

    # Change the bool values to more user-friendly characters
    if consolidated_issue.linked_to_project:
        linked_to_project = "🟢"
    else:
        linked_to_project = "🔴"

    # Generate the markdown line for the issue
    md_issue_line = (f"|{organization_name} | {repository_name} | [#{number} - {title}]({page_filename}) |"
                     f" {linked_to_project} | {status} |[GitHub link]({url}) |\n")

    return md_issue_line


def group_issues_by_milestone(consolidated_issues_data: list) -> Dict[str, List[ConsolidatedIssue]]:
    """
        Groups issues by their milestone.

        @param consolidated_issues_data: A list of all consolidated issues.

        @return: A dictionary where each key is a milestone title and the value is a list of issues
         under that milestone.
    """

    # Initialize a dictionary to store all milestones
    milestones = {}

    # Create a consolidated issue objects from the data
    for consolidated_issue_data in consolidated_issues_data:
        consolidated_issue = ConsolidatedIssue()
        consolidated_issue.load_from_data(consolidated_issue_data)

        # Prepare the structure for correct grouping the issues with same milestone
        if consolidated_issue.milestone is not None:
            milestone_title = f"{consolidated_issue.milestone.title}"
        else:
            milestone_title = "No milestone"

        # Create a new milestone structure, if it does not exist
        if milestone_title not in milestones:
            milestones[milestone_title] = []

        # Add the issue to the correct milestone
        milestones[milestone_title].append(consolidated_issue)

    return milestones


def generate_milestone_block(milestone_table_header: str, milestone_title: str, issue_lines: List[str]) -> str:
    """
        Generates a markdown block for a given milestone and its features.

        @param milestone_table_header: The table header for the milestone block.
        @param milestone_title: The title of the milestone.
        @param issue_lines: A list of markdown lines, each representing a feature.

        @return: A string representing the markdown block for the milestone.
    """

    milestone_block = f"\n### {milestone_title}\n" + milestone_table_header + "".join(issue_lines)

    return milestone_block


def process_issues(milestones: Dict[str, List[ConsolidatedIssue]],
                   issue_page_template: str,
                   milestones_as_chapters: bool) -> str:
    """
        Processes features and generates a markdown file for each feature.

        @param milestones: A dictionary where each key is a milestone title and the value is a list of features under that milestone.
        @param issue_page_template: The string template for the single page markdown file.
        @param milestones_as_chapters: A boolean switch indicating whether milestones should be treated as chapters.

        @return: A string containing all the generated markdown blocks for the processed features.
    """

    issue_markdown_content = ""
    milestone_table_header = """| Organization name     | Repository name | Issue 'Number - Title'  | Linked to project | Project status  |Issue URL   |
           |-----------------------|-----------------|---------------------------|---------|------|-----|
           """

    # If milestones are not treated as chapters, add table header
    if not milestones_as_chapters:
        issue_markdown_content += "\n" + milestone_table_header

    for milestone_title, consolidated_issues in sorted(milestones.items()):
        # Generate issue lines
        issue_lines = [generate_issue_line(issue) for issue in consolidated_issues]

        # Generate tables based on using config bool value of `milestones_as_chapters`
        if milestones_as_chapters:
            issue_markdown_content += generate_milestone_block(milestone_table_header, milestone_title, issue_lines)
        else:
            issue_markdown_content += "\n".join(issue_lines)

        # Generate markdown file for every issue
        for consolidated_issue in consolidated_issues:
            generate_md_issue_page(issue_page_template, consolidated_issue, OUTPUT_DIRECTORY)

    return issue_markdown_content


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

        # Create Markdown string for the table of contents
        toc_link = f"{indentation}- [{title}](#{anchor_link})"

        toc.append(toc_link)

    # ToC into single string separated
    toc_string = "\n".join(toc)

    return toc_string


def generate_index_page(issue_markdown_content: str, template_index_page: str, milestones_as_chapters: bool) -> None:
    """
        Generates an index summary markdown page for all features.

        @param issue_markdown_content: A string containing all the generated markdown blocks for the features.
        @param template_index_page: The string template for the index markdown page.
        @param milestones_as_chapters: A boolean switch indicating whether milestones should be treated as chapters.

        @return: None
    """

    # Prepare issues replacement for the index page
    issues_replacement = {
        "issues": issue_markdown_content
    }

    # Replace the issue placeholders in the index template
    index_page_content = replace_template_placeholders(template_index_page, issues_replacement)

    # Generate table of contents, if config value of `milestones_as_chapters` is True
    table_of_contents = generate_table_of_contents(index_page_content) if milestones_as_chapters else ""

    # Prepare additional replacements for the index page
    replacements = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "table-of-contents": table_of_contents
    }

    # Second wave of replacing placeholders in the index template
    index_page = replace_template_placeholders(index_page_content, replacements)

    # Create an index page file
    with open(os.path.join(OUTPUT_DIRECTORY, "_index.md"), 'w', encoding='utf-8') as index_file:
        index_file.write(index_page)

    print("Generated _index.md.")


def main() -> None:
    print("Script for converting consolidated issues into md pages started.")

    # Get environment variable, if the milestones should be treated as chapters
    milestones_as_chapters = os.getenv('MILESTONES_AS_CHAPTERS')
    milestones_as_chapters = milestones_as_chapters.lower() == 'true'

    # Check if the output directory exists and create it if not
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(os.path.join(current_dir, OUTPUT_DIRECTORY), current_dir)

    print("Starting the issue page generation process.")

    # Load consolidated issue data and page templates
    with open(CONSOLIDATION_FILE, 'r', encoding='utf-8') as consolidation_json_file:
        consolidated_issues_data = json.load(consolidation_json_file)

    with open(ISSUE_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as issue_page_template_file:
        issue_page_template = issue_page_template_file.read()

    with open(INDEX_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as idx_page_template_file:
        index_page_template = idx_page_template_file.read()

    # Organize consolidated issues data by milestones
    milestones = group_issues_by_milestone(consolidated_issues_data)

    # Process issues and generate Markdown pages
    issue_markdown_content = process_issues(milestones, issue_page_template, milestones_as_chapters)

    # Generate index page
    generate_index_page(issue_markdown_content, index_page_template, milestones_as_chapters)

    print(f"Living documentation generated at: {os.path.join(current_dir, OUTPUT_DIRECTORY_ROOT)}")

    print("Script for converting consolidated issues into md pages ended.")


if __name__ == "__main__":
    main()
