# Repository delivery

Updated 22 September 2026.

Target: https://github.com/robdin/fitness

Delivery branch: codex/fitness-os-pilots

The system, research and six prototype videos were first committed locally on 20 September. The command-line push could not authenticate. On 22 September, the connected GitHub app verified write access, allowing repository delivery through authenticated GitHub operations. The previously empty remote was initialized with the existing runtime exclusions so the complete system can be reviewed and merged through a pull request to main.

Use the repository's pull request and Actions records for the current merge and check status. The earlier downloaded archive is a dated snapshot and does not automatically reflect later repository changes. The original local history is retained separately when the imported branch is synchronized.

The reference repository https://github.com/robdin/turuan has not received a code-level audit. Its supplied guide was analyzed, but its source was not copied. That review remains a separate task; access failure observed on 20 September is not a claim about the current connected app's permissions. No credentials should be pasted into repository files.

## Downloaded handoff

The companion Fitness_OS_Starter_Package.zip contains the committed source, documentation, research and portable six-variant gallery under fitness-os/. Open examples/pilot-review/index.html after extracting it. The package also includes history/fitness-os.bundle, retaining the local branch history.

To restore the committed branch from that bundle into a new folder:

~~~bash
git clone --branch codex/fitness-os-pilots /absolute/path/fitness-os.bundle fitness-os-restored
cd fitness-os-restored
git remote set-url origin https://github.com/robdin/fitness.git
git push -u origin codex/fitness-os-pilots
~~~

The last command requires your normal GitHub authentication and repository permission. Do not force-push. If someone has populated the target in the meantime, fetch and inspect the new work before integrating.

The archive excludes runtime databases, raw recordings, credentials, generated temporary tests and customer information. The six included videos are explicitly silent prototypes, not approved public releases or audience-test results.
