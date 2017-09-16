import subprocess
import os
from bedrock.analytics.utils import Algorithm
import pandas as pd
import logging
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr
import csv

def check_valid_formula(formula):
    # TODO: Look at `patsy` for helper function to validate more fully
    if (len(formula.split('~')) < 2):
        logging.error("Formula does not have ~")
        return False

class Stan_GLM(Algorithm):
    def __init__(self):
        super(Stan_GLM, self).__init__()
        self.parameters = []
        self.inputs = ['matrix.csv','features.txt']
        self.outputs = ['matrix.csv','prior_summary.txt']
        self.name ='Stan_GLM'
        self.type = 'GLM'
        self.description = 'Performs Stan_GLM analysis on the input dataset.'

        self.parameters_spec = [
            { "name" : "Formula", "attrname" : "formula", "value" : "", "type" : "input" },
            { "name" : "GLM family", "attrname" : "family", "value" : "", "type" : "input" },
            { "name" : "chains", "attrname" : "chains" , "value" : "", "type" : "input"},
            { "name" : "iter", "attrname" : "iter" , "value" : "", "type" : "input"},
            { "name" : "prior", "attrname" : "prior" , "value" : "", "type" : "input"},
            { "name" : "prior_intercept", "attrname" : "prior_intercept" , "value" : "", "type" : "input"}
        ]

    def check_parameters(self):
        logging.error("Started check parms")
        super(Stan_GLM, self).check_parameters()

        if(check_valid_formula(self.formula) == False):
            return False

        self.family = self.family.lower()

        if self.family == 'logit':
            self.family = 'binomial(link = "logit")'
        elif self.family == 'gaussian':
            self.family = 'gaussian(link = "identity")'
        else:
            logging.error("GLM family {} not supported".format(self.family))
            return False

        return True
    def __build_df__(self, filepath):
        featuresPath = filepath['features.txt']['rootdir'] + 'features.txt'
        matrixPath = filepath['matrix.csv']['rootdir'] + 'matrix.csv'
        df = pd.read_csv(matrixPath, header=-1)
        featuresList = pd.read_csv(featuresPath, header=-1)

        df.columns = featuresList.T.values[0]

        return df

    def compute(self, filepath, **kwargs):
        rstan = importr("rstan")
        rstanarm = importr("rstanarm")
        pandas2ri.activate()

        df = self.__build_df__(filepath)
        rdf = pandas2ri.py2ri(df)

        robjects.globalenv["rdf"] = rdf

        rglmString = "output = stan_glm({}, data=rdf".format(self.formula)

        if hasattr(self, 'family') and self.family != "":
            rglmString += ", family = {}".format(self.family)
        else:
            rglmString += ', family = binomial(link = "logit")'

        if hasattr(self, 'chains') and self.chains != "":
            rglmString += ", chains = {}".format(self.chains)

        if hasattr(self, 'iter') and self.iter != "":
            rglmString += ", iter = {}".format(self.iter)

        if hasattr(self, 'prior') and self.prior != "":
            rglmString += ", prior = {}".format(self.prior)

        if hasattr(self, 'prior_intercept') and self.prior_intercept != "":
            rglmString += ", prior_intercept = {}".format(self.prior_intercept)

        rglmString += ")"

        logging.error(rglmString)
        r(rglmString)
        prior_summary_txt = r('ps<-prior_summary(output)')
        summary_txt = r('s<-summary(output)')
        summary = r('data.frame(s)')
        summary_list = list(summary.to_csv().split('\n'))
        logging.error(summary_list)
        logging.error(summary.to_csv().split('\n'))

        self.results = {'matrix.csv': list(csv.reader(summary.to_csv().split('\n'))),
                        'prior_summary.txt': [str(prior_summary_txt)]}
