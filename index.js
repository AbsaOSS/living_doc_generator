const { exec } = require('child_process');
const core = require('@actions/core');

async function run() {
    try {
        const githubToken = core.getInput('GITHUB_TOKEN');
        const projectStateMining = core.getInput('project-state-mining');
        const projectsTitleFilter = core.getInput('projects-title-filter');
        const milestonesAsChapters = core.getInput('milestones-as-chapters');
        const repositories = core.getInput('repositories');

        // Construct the command with the provided inputs
        const command = `python3 scripts/controller.py \
            --github-token "${githubToken}" \
            --project-state-mining "${projectStateMining}" \
            --projects-title-filter "${projectsTitleFilter}" \
            --milestones-as-chapters "${milestonesAsChapters}" \
            --repositories '${repositories}'`;

        // Running the Python script with an input
        exec(command, (error, stdout, stderr) => {
            if (error) {
                core.setFailed(`Execution error: ${error}`);
                return;
            }
            if (stderr) {
                core.setFailed(`Execution stderr: ${stderr}`);
                return;
            }
            console.log(`Python script output: ${stdout}`);

            core.setOutput("documentation-path", stdout.trim());
        });
    } catch (error) {
        core.setFailed(`Action failed with error ${error}`);
    }
}

run();
