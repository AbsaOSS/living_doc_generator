import os
import sys
import subprocess


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
        print(f"Error running {script_name}: {e.stderr}")


def main():
    if len(sys.argv) < 2:
        print("This script requires an input variable")
        sys.exit(1)

    input1 = sys.argv[1]
    env_vars = {'INPUT_VAR': input1}

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
    run_script('convert_features_to_pages.py', env_vars)


if __name__ == '__main__':
    main()
