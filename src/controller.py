import os
import subprocess
import argparse
import sys
import re


def extract_args():
    """ Extract and return the required arguments using argparse. """
    parser = argparse.ArgumentParser(description='Generate Living Documentation from GitHub repositories.')

    parser.add_argument('--github-token', required=True, help='GitHub token for authentication.')
    parser.add_argument('--project-state-mining', required=True, help='Enable or disable mining of project state data.')
    parser.add_argument('--projects-title-filter', required=True, help='Filter projects by titles. Provide a list of project titles.')
    parser.add_argument('--milestones-as-chapters', required=True, help='Treat milestones as chapters in the generated documentation.')
    parser.add_argument('--repositories', required=True, help='JSON string defining the repositories to be included in the documentation generation.')

    args = parser.parse_args()

    env_vars = {
        'GITHUB_TOKEN': args.github_token,
        'PROJECT_STATE_MINING': args.project_state_mining,
        'PROJECTS_TITLE_FILTER': args.projects_title_filter,
        'MILESTONES_AS_CHAPTERS': args.milestones_as_chapters,
        'REPOSITORIES': args.repositories
    }

    return env_vars


def run_script(script_name, env_vars):
    """ Helper function to run a Python script with environment variables using subprocess """
    try:
        # Setting up the environment for subprocess
        env = os.environ.copy()
        env.update(env_vars)

        # Running the script with updated environment
        result = subprocess.run(['python3', script_name], env=env, text=True, capture_output=True, check=True)
        print(f"Output from {script_name}: {result.stdout}")

    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: \n{e.stdout}\n{e.stderr}")
        sys.exit(1)


def main():
    print("Extracting arguments from command line.")
    env_vars = extract_args()

    # Clean environment before mining
    print("Data mining for Living Documentation")
    run_script('clean_env_before_mining.py', env_vars)

    # Data mine GitHub features from repository
    print("Downloading issues from GitHub")
    run_script('github_query_issues.py', env_vars)

    # Data mine GitHub project's state
    print("Downloading project's state")
    run_script('github_query_project_state.py', env_vars)

    # Consolidate all feature data together
    print("Consolidating mined feature data")
    run_script('consolidate_feature_data.py', env_vars)

    # Generate markdown pages
    print("Converting features to markdown pages")
    output_path = run_script('convert_features_to_pages.py', env_vars)

    # Output the documentation path
    print(output_path)


if __name__ == '__main__':
    print("Starting Living Documentation generation.")
    main()
    print("Living Documentation generation completed.")
