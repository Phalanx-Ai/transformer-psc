## Transform Czech ZIP (PSČ) to district/county

Table with ZIP codes (from Czech Republic) contains enough information to fill columns with District and County.

Be aware that one ZIP code can be part of multiple districts/counties. Fortunately, it only happens for smallest villages where impact on your results can be ignored. 

## Configuration

Data transformation is applied to all of the input/output mappings. A configuration also consists of following parameters:

* Name of the existing column with ZIP/PSČ code (`column_psc`)
* Name of the new column with districts (`column_district`) - When parameter is not defined, the value of district is not filled.
* Name of the new column with counties (`column_county`) - When parameter is not defined, the value of county is not filled.

## Output

Output tables as defined in the configuration with new columns for district and/or county.
