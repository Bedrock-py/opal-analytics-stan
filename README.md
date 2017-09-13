opal-analytics-stan
=========================

## Installation

`pip install git+https://github.com/Bedrock-py/opal-analytics-stan.git`

## Parameters Spec for Bedrock

```
self.parameters_spec = [
    { "name" : "Formula", "attrname" : "formula", "value" : "decision0d1c ~ condition", "type" : "input" },
    { "name" : "GLM family", "attrname" : "family", "value" : 'binomial(link = "logit")', "type" : "input" },
    { "name" : "chains", "attrname" : "chains" , "value" : "3", "type" : "input"},
    { "name" : "iter", "attrname" : "iter" , "value" : "3000", "type" : "input"},
    { "name" : "prior", "attrname" : "prior" , "value" : "", "type" : "input"},
    { "name" : "prior_intercept", "attrname" : "prior_intercept" , "value" : "", "type" : "input"}
]
```

* `formula` A R-style formula for regression given as a string
* `family` binomial(link = "logit") is the only family supported currently, future updates will add more families
* `chains` number of chains to run
* `iter` number of iterations
* `prior` expected format: student_t(-0.186, 0.036, df = 7)
* `prior intercept` expected fromat: student_t(0.662, 0.196, df = 7)

parameters derived from https://github.com/gallup/NGS2/blob/master/NGS2_WITNESS_Cycle1_bayesian_exp1.R

## Requires a Matrix with the following files

* `matrix.csv` The full matrix with both endogenous and exogenous variables
* `features.txt` A list of column names for the matrix (one name per row)

## Outputs the following files

`prior_summary.txt` print out of prior_summary() function (rstanarm)
`summary.txt` print out of summary() function (rstanarm)
