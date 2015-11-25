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

*Reference:* Irving D, Simmonds I (2015).
[A novel approach to diagnosing Southern Hemisphere planetary wave activity and its influence on regional climate variability](http://journals.ametsoc.org/doi/abs/10.1175/JCLI-D-15-0287.1).
*Journal of Climate*. 28, 9041-9057. doi:10.1175/JCLI-D-15-0287.1.

* Config file: `zw_config.mk`
* Basic analyses that underpin the rest: `zw_base.mk`
* Wave envelope and Fourier transform analysis: `zw_envelope.mk`
* Composite creation and plotting: `zw_composites.mk`
* Compare various indices: `zw_index_comparison.mk`


#### PSA pattern analysis

*Reference:* Irving D, Simmonds I (in preparation).
A new method for identifying the Pacific-South American pattern and its influence on regional climate variability.

* Config file: `psa_config.mk`
* Everything else: `psa_base.mk`
