const path = require('path');
const { exec } = require('child_process');
const core = require('@actions/core');
const fs = require('fs');

async function run() {
    try {
        const githubToken = core.getInput('GITHUB_TOKEN');
        const projectStateMining = core.getInput('project-state-mining');
        const projectsTitleFilter = core.getInput('projects-title-filter');
        const milestonesAsChapters = core.getInput('milestones-as-chapters');
        const repositories = core.getInput('repositories');

        // Construct the path to the Python script
        const scriptPath = path.join(__dirname, 'controller.py');

        // Construct the command with the provided inputs
        const command = `python3 ${scriptPath} \
            --github-token "${githubToken}" \
            --project-state-mining "${projectStateMining}" \
            --projects-title-filter "${projectsTitleFilter}" \
            --milestones-as-chapters "${milestonesAsChapters}" \
            --repositories '${repositories}'`;

        // Running the Python script with an input
        exec(command, { cwd: __dirname }, (error, stdout, stderr) => {
            core.info(`Python script output: ${stdout}`);

            if (error) {
                core.error(`Error executing script: ${error.message}`)
                core.error(`Error code: ${error.code}`);
                core.error(`Error signal: ${error.signal}`);
                core.error(`Error stack: ${error.stack}`);

                core.setFailed(`Execution error.`);
            }
            if (stderr) {
                core.setFailed(`Execution stderr: ${stderr}`);
            }

            try {
                const documentationPath = extractPath(stdout);
                core.info(`Setting output ['documentation-path': '${documentationPath}']`)
                core.setOutput("documentation-path", documentationPath);
            } catch (extractError) {
                core.setFailed(`Error extracting documentation path: ${extractError.message}`);
            }
        });
    } catch (error) {
        core.setFailed(`Action failed with error ${error}`);
    }
}

function extractPath(output) {
    // Regular expression to find the line and extract the path
    const match = output.match(/Living documentation generated on the path:\s*(.*)/);
    if (match) {
        return match[1].trim();
    } else {
        throw new Error("Generated path to Living documentation not found.");
    }
}

run();
