import subprocess
import os
from bedrock.analytics.utils import Algorithm
import pandas as pd
import logging
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

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
        self.outputs = ['prior_summary.txt', 'summary.txt']
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

#     def check_parameters(self):
#         logging.error("Started check parms")
#         super(Stan_GLM, self).check_parameters()

#         if(check_valid_formula(self.formula) == False):
#             return False

#         self.family = self.family.lower()

#         if (self.family != 'binomial(link = "logit")' and self.family != 'gaussian(link = "identity")'):
#             logging.error("GLM family {} not supported".format(self.family))
#             return False
            
#        return True
    def __build_df__(self, filepath):
        featuresPath = filepath['features.txt']['rootdir'] + 'features.txt'
        matrixPath = filepath['matrix.csv']['rootdir'] + 'matrix.csv'
        df = pd.read_csv(matrixPath, header=-1)
        featuresList = pd.read_csv(featuresPath, header=-1)

        df.columns = featuresList.T.values[0]

        return df


    def compute(self, filepath, **kwargs):
        
        print "load rstanarm"
        
        rstan = importr("rstan")
        rstanarm = importr("rstanarm")

        
        df = self.__build_df__(filepath)
        rdf = pandas2ri.py2ri(df)
        
        robjects.globalenv["rdf"] = rdf
        
        rglmString = output = "stan_glm({}, data=MyData,family = {}, chains = {}, iter = {})"
        
        rglmStringFormatted = rglmString.format(kwargs["formula"],kwargs["family"],kwargs["chains"], kwargs["iter"], kwargs["prior"], kwargs["prior_intercept"])
              
        
        rpy2.robjects.r('output = stan_glm(decision0d1c~round_num, data=rdf,family = binomial(link = "logit"), chains = 3, iter = 3000)')
        prior_summary = rpy2.robjects.r('prior_summary<-prior_summary(output)')
        summary = rpy2.robjects.r('summary<-summary(output)')

        self.results = {'prior_summary.txt': prior_summary, 'summary.txt': summary}
