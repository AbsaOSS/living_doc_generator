const { exec } = require('child_process');
const core = require('@actions/core');

async function run() {
    try {
        const input1 = core.getInput('input1');

        // Running the Python script with an input
        exec(`python3 scripts/controller.py "${input1}"`, (error, stdout, stderr) => {
            if (error) {
                core.setFailed(`Execution error: ${error}`);
                return;
            }
            if (stderr) {
                core.setFailed(`Execution stderr: ${stderr}`);
                return;
            }
            console.log(`Python script output: ${stdout}`);
            core.setOutput("output1", stdout.trim());
        });
    } catch (error) {
        core.setFailed(`Action failed with error ${error}`);
    }
}

run();
