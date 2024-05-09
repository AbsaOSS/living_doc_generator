# Living documentation generator
A tool designed to data-mine GitHub repositories for issues containing project documentation (e.g. tagged with feature-related labels). This tool automatically generates comprehensive living documentation in markdown format, providing detailed feature overview pages and in-depth feature descriptions.

## Motivation
TODO

## Usage
### Prerequisites
Before we begin, ensure you have a GitHub Token with permission to fetch repository data such as Issues and Pull Requests.

### Adding the Action to Your Workflow

Add the following step to your GitHub workflow (in example are used non-default values):

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.1.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
  with:
    TODO
```

### Configure the Action
Configure the action by customizing the following parameters based on your needs:

- **GITHUB_TOKEN** (required): Your GitHub token for authentication. Store it as a secret and reference it in the workflow file as secrets.GITHUB_TOKEN.
- **TODO** (required): TODO

## Setup
If you need to build the action locally, follow these steps:

#### Prepare the Environment
```
node --version
python3 --version
```

#### Install Node.js Dependencies
```
npm install
```

#### Compile or Prepare the JavaScript Files
```
npm run build
```

#### Set Up Python Environment
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run unit test
#### Launch unit tests
```
cd tests
pytest
```

#### To run specific tests or get verbose output:
```
pytest -v  # Verbose mode
pytest path/to/test_file.py  # Run specific test file
```

#### To check Test Coverage:
```
pytest --cov=../scripts
```

#### After running the tests
```
deactivate
```

#### Commit Changes
After testing and ensuring that everything is functioning as expected, prepare your files for deployment:

```
git add action.yml dist/index.js  # Adjust paths as needed
git commit -m "Prepare GitHub Action for deployment"
git push
```

### Deployment
This project uses GitHub Actions for deployment draft creation. The deployment process is semi-automated by a workflow defined in `.github/workflows/release_draft.yml`.

- **Trigger the workflow**: The `release_draft.yml` workflow is triggered on workflow_dispatch.
- **Create a new draft release**: The workflow creates a new draft release in the repository.
- **Finalize the release draft**: Edit the draft release to add a title, description, and any other necessary details related to GitHub Action.
- **Publish the release**: Once the draft is ready, publish the release to make it available to the public.


## Features

TODO - project states scan for Features


### Contribution Guidelines

We welcome contributions to the Living Documentation Generator! Whether you're fixing bugs, improving documentation, or proposing new features, your help is appreciated.

#### How to Contribute
- **Submit Pull Requests**: Feel free to fork the repository, make changes, and submit a pull request. Please ensure your code adheres to the existing style and all tests pass.
- **Report Issues**: If you encounter any bugs or issues, please report them via the repository's [Issues page](https://github.com/AbsaOSS/living-doc-generator/issues).
- **Suggest Enhancements**: Have ideas on how to make this action better? Open an issue to suggest enhancements.

Before contributing, please review our [contribution guidelines](https://github.com/AbsaOSS/living-doc-generator/blob/master/CONTRIBUTING.md) for more detailed information.

### License Information

This project is licensed under the Apache License 2.0. It is a liberal license that allows you great freedom in using, modifying, and distributing this software, while also providing an express grant of patent rights from contributors to users.

For more details, see the [LICENSE](https://github.com/AbsaOSS/living-doc-generator/blob/master/LICENSE) file in the repository.

### Contact or Support Information

If you need help with using or contributing to Living Documentation Generator Action, or if you have any questions or feedback, don't hesitate to reach out:

- **Issue Tracker**: For technical issues or feature requests, use the [GitHub Issues page](https://github.com/AbsaOSS/living-doc-generator/issues).
- **Discussion Forum**: For general questions and discussions, join our [GitHub Discussions forum](https://github.com/AbsaOSS/living-doc-generator/discussions).

### FAQs
TODO
