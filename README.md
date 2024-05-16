# Living documentation generator

- [Motivation](#motivation)
- [Usage](#usage)
    - [Prerequisites](#prerequisites)
    - [Adding the Action to Your Workflow](#adding-the-action-to-your-workflow)
- [Action Configuration](#action-configuration)
    - [Environment Variables](#environment-variables)
    - [Inputs](#inputs)
    - [Features de/activation](#features-deactivation)
    - [Features configuration](#features-configuration)
    - [Page generator options](#page-generator-options)
- [Action Outputs](#action-outputs)
- [Project Setup](#project-setup)
- [Run unit test](#run-unit-test)
- [Deployment](#deployment)
- [Features](#features)
    - [Data Mining from GitHub Repositories](#data-mining-from-github-repositories)
    - [Data Mining from GitHub Projects](#data-mining-from-github-projects)
    - [Living Documentation Page Generation](#living-documentation-page-generation)
- [Contribution Guidelines](#contribution-guidelines)
- [License Information](#license-information)
- [Contact or Support Information](#contact-or-support-information)

A tool designed to data-mine GitHub repositories for issues containing project documentation (e.g. tagged with feature-related labels). This tool automatically generates comprehensive living documentation in markdown format, providing detailed feature overview pages and in-depth feature descriptions.

## Motivation
Addresses the need for continuously updated documentation accessible to all team members and stakeholders. Achieves this by extracting information directly from GitHub issues and integrating this functionality to deliver real-time, markdown-formatted output. Ensures everyone has the most current project details, fostering better communication and efficiency throughout development.

## Usage
### Prerequisites
Before we begin, ensure you have a GitHub Token with permission to fetch repository data such as Issues and Pull Requests.

### Adding the Action to Your Workflow

See the default action step definition:

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.1.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
  with:
    repositories: '[
      {
        "orgName": "fin-services",
        "repoName": "investment-app",
        "queryLabels": ["feature", "enhancement"]
      },
      {
        "orgName": "health-analytics",
        "repoName": "patient-data-analysis",
        "queryLabels": ["functionality"]
      },
      {
        "orgName": "open-source-initiative",
        "repoName": "community-driven-project",
        "queryLabels": ["improvement"]
      }
    ]'
  ```

See the full example of action step definition (in example are used non-default values):

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.1.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
  with:
    # features de/activation
    project-state-mining: true
    
    # features configuration
    projects-title-filter": ["Community Outreach Initiatives", "Health Data Analysis"]
    
    # page generator options
    milestones-as-chapters: true

    # inputs
    repositories: '[
      {
        "orgName": "fin-services",
        "repoName": "investment-app",
        "queryLabels": ["feature", "enhancement"]
      },
      {
        "orgName": "health-analytics",
        "repoName": "patient-data-analysis",
        "queryLabels": ["functionality"]
      },
      {
        "orgName": "open-source-initiative",
        "repoName": "community-driven-project",
        "queryLabels": ["improvement"]
      }
    ]'
```



## Action Configuration
Configure the action by customizing the following parameters based on your needs:

### Environment Variables
- **GITHUB_TOKEN** (required):
  - **Description**: Your GitHub token for authentication. 
  - **Usage**: Store it as a secret and reference it in the workflow file using  `${{ secrets.GITHUB_TOKEN }}`.
  - **Example**:
    ```yaml
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```
    
### Inputs
- **repositories** (required)
  - **Description**: A JSON string defining the repositories to be included in the documentation generation.
  - **Usage**: List each repository with its organization name, repository name, and query labels.
  - **Example**:
    ```yaml
    with:
      repositories: '[
        {
          "orgName": "fin-services",
          "repoName": "investment-app",
          "queryLabels": ["feature", "enhancement"]
        },
        {
          "orgName": "health-analytics",
          "repoName": "patient-data-analysis",
          "queryLabels": ["functionality"]
        },
        {
          "orgName": "open-source-initiative",
          "repoName": "community-driven-project",
          "queryLabels": ["improvement"]
        }
      ]'
    ```

### Features de/activation
- **project-state-mining** (optional, `default: true`)
  - **Description**: Enables or disables the mining of project state data from [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects).
  - **Usage**: Set to false to deactivate.
  - **Example**:
    ```yaml
    with:
      project-state-mining: false
    ```
    
### Features configuration
- **projects-title-filter** (optional, `default: []`)
  - **Description**: Filters the projects by titles. Only projects with these titles will be considered.
  - **Usage**: Provide a list of project titles to filter.
  - **Example**:
    ```yaml
    with:
      projects-title-filter: ["Community Outreach Initiatives", "Health Data Analysis"]
    ```

### Page generator options 
- **milestones-as-chapters** (optional, `default: false`)
  - **Description**: When set to **true**, milestones in the projects will be treated as chapters in the generated documentation.
  - **Usage**: Set to **true** to enable this feature.
  - **Example**:
    ```yaml
    with:
      milestones-as-chapters: true
    ```

## Action Outputs
The Living Documentation Generator action provides a key output that allows users to locate and access the generated documentation easily. This output can be utilized in various ways within your CI/CD pipeline to ensure the documentation is effectively distributed and accessible.

- **documentation-path**
  - **Description**: This output provides the path to the directory where the generated living documentation files are stored.
  - **Usage**: 
   ``` yaml
    - name: Generate Living Documentation
      id: generate_doc
      ... rest of the action definition ...
      
    - name: Output Documentation Path
      run: echo "Generated documentation path: ${{ steps.generate_doc.outputs.documentation-path }}"            
    ```

## Project Setup
If you need to build the action locally, follow these steps:

### Prepare the Environment
```
node --version
python3 --version
```

### Install Node.js Dependencies
```
npm install
```

### Compile or Prepare the JavaScript Files
```
npm run build
```

### Set Up Python Environment
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run unit test
TODO - check this chapter and update by latest state
### Launch unit tests
```
pytest
```

### To run specific tests or get verbose output:
```
pytest -v  # Verbose mode
pytest path/to/test_file.py  # Run specific test file
```

### To check Test Coverage:
```
pytest --cov=../scripts
```

### After running the tests
```
deactivate
```

### Commit Changes
After testing and ensuring that everything is functioning as expected, prepare your files for deployment:

```
git add action.yml dist/index.js  # Adjust paths as needed
git commit -m "Prepare GitHub Action for deployment"
git push
```

## Deployment
This project uses GitHub Actions for deployment draft creation. The deployment process is semi-automated by a workflow defined in `.github/workflows/release_draft.yml`.

- **Trigger the workflow**: The `release_draft.yml` workflow is triggered on workflow_dispatch.
- **Create a new draft release**: The workflow creates a new draft release in the repository.
- **Finalize the release draft**: Edit the draft release to add a title, description, and any other necessary details related to GitHub Action.
- **Publish the release**: Once the draft is ready, publish the release to make it available to the public.


## Features

### Data Mining from GitHub Repositories

This feature allows you to define which repositories should be included in the living documentation process. By specifying repositories, you can focus on the most relevant projects for your documentation needs.

- **Default Behavior**: By default, the action will include all repositories defined in the repositories input parameter. Each repository is defined with its organization name, repository name, and query labels.

### Data Mining from GitHub Projects

This feature allows you to define which projects should be included in the living documentation process. By specifying projects, you can focus on the most relevant projects for your documentation needs.

- **Default Behavior**: By default, the action will include all projects defined in the repositories. This information is provided by the GitHub API.
- **Non-default Example**: Use available options to customize which projects are included in the documentation.
  - `project-state-mining: false` deactivates the mining of project state data from GitHub Projects. If set to **false**, project state data will not be included in the generated documentation and project related configuration options will be ignored. 
  - `projects-title-filter: ["Community Outreach Initiatives", "Health Data Analysis"]` filters the projects by titles, including only projects with these titles.

### Living Documentation Page Generation

The goal is to provide a straightforward view of all issues in a single table, making it easy to see the overall status and details of issues across repositories.

- **Default Behavior**: By default, the action generates a single table that lists all issues from the defined repositories.
- **Non-default Example**: Use available options to customize the output, such as grouping issues by milestone.
  - `milestones-as-chapters: true` controls whether milestones are treated as chapters in the generated documentation.

---
## Contribution Guidelines

We welcome contributions to the Living Documentation Generator! Whether you're fixing bugs, improving documentation, or proposing new features, your help is appreciated.

#### How to Contribute
Before contributing, please review our [contribution guidelines](https://github.com/AbsaOSS/living-doc-generator/blob/master/CONTRIBUTING.md) for more detailed information.

### License Information

This project is licensed under the Apache License 2.0. It is a liberal license that allows you great freedom in using, modifying, and distributing this software, while also providing an express grant of patent rights from contributors to users.

For more details, see the [LICENSE](https://github.com/AbsaOSS/living-doc-generator/blob/master/LICENSE) file in the repository.

### Contact or Support Information

If you need help with using or contributing to Living Documentation Generator Action, or if you have any questions or feedback, don't hesitate to reach out:

- **Issue Tracker**: For technical issues or feature requests, use the [GitHub Issues page](https://github.com/AbsaOSS/living-doc-generator/issues).
- **Discussion Forum**: For general questions and discussions, join our [GitHub Discussions forum](https://github.com/AbsaOSS/living-doc-generator/discussions).
