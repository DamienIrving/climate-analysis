## Workflows

This directory contains the makefiles used to execute the analyses described below.
To execute any of the workflows:  

1. Update the relevant `config.mk` file with your directory structure and desired options/settings
2. Replace the `TARGET` in the `config.mk` file with a target taken from one of the other
makefiles related to that workflow
3. Run the workflow: e.g. `make -n -B -f zw_applications.mk`
(`-n` is a dry run where what would have been executed is just printed to the screen)
(`-B` forces all the steps to be executed, not just the ones that need updating)  

#### Zonal wave analysis

*Reference:* Irving DB, Simmonds I (in preparation).
Southern Hemisphere planetary wave activity and its influence on weather and climate extremes.

* Config file: `zw_config.mk`
* Workflow for basic climatology: `zw_climatology.mk`
* Workflow for detailed analysis of that climatology: `zw_applications.mk`

Note that `zw_tscale_analysis.mk` and `zw_tscale_analysis_config.mk`
were used in the initial scoping for the zonal wave analysis
but were not used to produce any of the results in the reference above

#### PSA pattern analysis

*Reference:* Irving DB, Simmonds I (in preparation).
The Pacific-South America Pattern: a climatology

* Config file: `psa_config.mk`
* Workflow for basic climatology: `psa_climatology.mk`
