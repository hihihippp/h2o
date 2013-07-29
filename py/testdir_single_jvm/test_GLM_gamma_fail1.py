import unittest, random, sys, time
sys.path.extend(['.','..','py'])
import h2o, h2o_cmd, h2o_glm, h2o_hosts

class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global SEED, localhost
        SEED = h2o.setup_random_seed()
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(node_count=1)
        else:
            h2o_hosts.build_cloud_with_hosts(node_count=1)

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_GLM_gamma_fail1(self):
        csvPathname = h2o.find_dataset('UCI/UCI-large/covtype/covtype.data')
        parseKey = h2o_cmd.parseFile(csvPathname=csvPathname)
        for trial in range(5):
            kwargs = {
                'standardize': 0, 
                'family': 'gamma', 
                'link': 'familyDefault', 
                'y': 54, 
                'lambda': 0.0001,
                'alpha': 0.5, 
                'max_iter': 25, 
                'n_folds': 1, 
            }
            start = time.time()
            glm = h2o_cmd.runGLMOnly(timeoutSecs=120, parseKey=parseKey, **kwargs)
            print "glm end on ", csvPathname, 'took', time.time() - start, 'seconds'

            # if we hit the max_iter, that means it probably didn't converge. should be 1-maxExpectedIter
            h2o_glm.simpleCheckGLM(self, glm, None, maxExpectedIterations=kwargs['max_iter']-2, **kwargs)
            print "Trial #", trial, "completed\n"


if __name__ == '__main__':
    h2o.unit_main()