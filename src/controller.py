import os
import subprocess
import argparse
import sys


def extract_args():
    """ Extract and return the required arguments using argparse. """
    parser = argparse.ArgumentParser(description='Generate Living Documentation from GitHub repositories.')

    parser.add_argument('--github-token', required=True, help='GitHub token for authentication.')
    parser.add_argument('--project-state-mining', required=True, help='Enable or disable mining of project state data.')
    parser.add_argument('--projects-title-filter', required=True, help='Filter projects by titles. Provide a list of project titles.')
    parser.add_argument('--milestones-as-chapters', required=True, help='Treat milestones as chapters in the generated documentation.')
    parser.add_argument('--repositories', required=True, help='JSON string defining the repositories to be included in the documentation generation.')
    parser.add_argument('--output-directory', type=str, required=False, default='../output', help='Output directory, which stores the generated documentation.')

    args = parser.parse_args()

    env_vars = {
        'GITHUB_TOKEN': args.github_token,
        'PROJECT_STATE_MINING': args.project_state_mining,
        'PROJECTS_TITLE_FILTER': args.projects_title_filter,
        'MILESTONES_AS_CHAPTERS': args.milestones_as_chapters,
        'REPOSITORIES': args.repositories,
        'OUTPUT_DIRECTORY': args.output_directory
    }

    return env_vars


def run_script(script_name, env):
    """ Helper function to run a Python script with environment variables using subprocess """
    try:
        # Running the python script with given environment variables
        result = subprocess.run(['python3', script_name], env=env, text=True, capture_output=True, check=True)
        print(f"Output from {script_name}: {result.stdout}")

    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: \n{e.stdout}\n{e.stderr}")
        sys.exit(1)


def main():
    print("Extracting arguments from command line.")
    env_vars = extract_args()

    # Create a local copy of the current environment variables
    local_env = os.environ.copy()

    # Add the script-specific environment variables to the local copy
    local_env.update(env_vars)

    print("Starting the Living Documentation Generator - mining phase")

    # Clean the environment before mining
    run_script('clean_env_before_mining.py', local_env)

    # Data mine GitHub features from repository
    run_script('github_query_issues.py', local_env)

    # Data mine GitHub project's state
    run_script('github_query_project_state.py', local_env)

    # Consolidate all feature data together
    run_script('consolidate_issue_data.py', local_env)

    # Generate markdown pages
    run_script('convert_issues_to_pages.py', local_env)


if __name__ == '__main__':
    print("Starting Living Documentation generation.")
    main()
    print("Living Documentation generation completed.")
