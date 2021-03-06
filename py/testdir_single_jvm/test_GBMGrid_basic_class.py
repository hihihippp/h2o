import unittest, time, sys
sys.path.extend(['.','..','py'])
import h2o, h2o_cmd, h2o_glm, h2o_hosts, h2o_import as h2i, h2o_jobs 

DO_CLASSIFICATION = True

class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global localhost
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(1)
        else:
            h2o_hosts.build_cloud_with_hosts(1)

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_GBMGrid_basic_benign(self):
        csvFilename = "benign.csv"
        print "\nStarting", csvFilename 
        csvPathname = 'logreg/' + csvFilename
        parseResult = h2i.import_parse(bucket='smalldata', path=csvPathname, hex_key=csvFilename + ".hex", schema='put')
        # columns start at 0
        # cols 0-13. 3 is output
        # no member id in this one
        
        # fails with n_folds
        print "Not doing n_folds with benign. Fails with 'unable to solve?'"
        # check the first in the models list. It should be the best
        colNames = [ 'STR','OBS','AGMT','FNDX','HIGD','DEG','CHK', 'AGP1','AGMN','NLV','LIV','WT','AGLP','MST' ]
        modelKey = 'GBMGrid_benign'

        # 'cols', 'ignored_cols_by_name', and 'ignored_cols' have to be exclusive
        params = {
            'destination_key': modelKey,
            'ignored_cols_by_name': 'STR',
            'learn_rate': '.1,.2',
            'ntrees': 2,
            'max_depth': 8,
            'min_rows': 1,
            'response': 'FNDX',
            'classification': 1 if DO_CLASSIFICATION else 0,
            }

        kwargs = params.copy()
        timeoutSecs = 1800
        start = time.time()
        GBMFirstResult = h2o_cmd.runGBM(parseResult=parseResult, noPoll=True,**kwargs)
        print "\nGBMFirstResult:", h2o.dump_json(GBMFirstResult)
        # no pattern waits for all
        h2o_jobs.pollWaitJobs(pattern=None, timeoutSecs=300, pollTimeoutSecs=10, retryDelaySecs=5)
        elapsed = time.time() - start
        print "GBM training completed in", elapsed, "seconds."

        gbmGridView = h2o.nodes[0].gbm_grid_view(job_key=GBMFirstResult['job_key'], destination_key=modelKey)
        print h2o.dump_json(gbmGridView)

        if 1==0:
            gbmTrainView = h2o_cmd.runGBMView(model_key=modelKey)
            # errrs from end of list? is that the last tree?
            errsLast = gbmTrainView['gbm_model']['errs'][-1]

            print "GBM 'errsLast'", errsLast
            if DO_CLASSIFICATION:
                cm = gbmTrainView['gbm_model']['cm']
                pctWrongTrain = h2o_gbm.pp_cm_summary(cm);
                print "\nTrain\n==========\n"
                print h2o_gbm.pp_cm(cm)
            else:
                print "GBMTrainView:", h2o.dump_json(gbmTrainView['gbm_model']['errs'])


    def test_GBMGrid_basic_prostate(self):
        csvFilename = "prostate.csv"
        print "\nStarting", csvFilename
        # columns start at 0
        csvPathname = 'logreg/' + csvFilename
        parseResult = h2i.import_parse(bucket='smalldata', path=csvPathname, hex_key=csvFilename + ".hex", schema='put')
        colNames = ['ID','CAPSULE','AGE','RACE','DPROS','DCAPS','PSA','VOL','GLEASON']

        modelKey = 'GBMGrid_prostate'
        # 'cols', 'ignored_cols_by_name', and 'ignored_cols' have to be exclusive
        params = {
            'destination_key': modelKey,
            'ignored_cols_by_name': 'ID',
            'learn_rate': .1,
            'ntrees': '2,4',
            'max_depth': 8,
            'min_rows': 1,
            'response': 'CAPSULE',
            'classification': 1 if DO_CLASSIFICATION else 0,
            }

        kwargs = params.copy()
        timeoutSecs = 1800
        start = time.time()
        GBMFirstResult = h2o_cmd.runGBM(parseResult=parseResult, noPoll=True,**kwargs)
        print "\nGBMFirstResult:", h2o.dump_json(GBMFirstResult)
        # no pattern waits for all
        h2o_jobs.pollWaitJobs(pattern=None, timeoutSecs=300, pollTimeoutSecs=10, retryDelaySecs=5)
        elapsed = time.time() - start
        print "GBM training completed in", elapsed, "seconds."

        gbmGridView = h2o.nodes[0].gbm_grid_view(job_key=GBMFirstResult['job_key'], destination_key=modelKey)
        print h2o.dump_json(gbmGridView)

        if 1==0:
            gbmTrainView = h2o_cmd.runGBMView(model_key=modelKey)
            # errrs from end of list? is that the last tree?
            errsLast = gbmTrainView['gbm_model']['errs'][-1]

            print "GBM 'errsLast'", errsLast
            if DO_CLASSIFICATION:
                cm = gbmTrainView['gbm_model']['cm']
                pctWrongTrain = h2o_gbm.pp_cm_summary(cm);
                print "\nTrain\n==========\n"
                print h2o_gbm.pp_cm(cm)
            else:
                print "GBMTrainView:", h2o.dump_json(gbmTrainView['gbm_model']['errs'])


if __name__ == '__main__':
    h2o.unit_main()
