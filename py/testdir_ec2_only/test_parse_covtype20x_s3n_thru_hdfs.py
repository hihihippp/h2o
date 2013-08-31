import unittest, time, sys, random
sys.path.extend(['.','..','py'])
import h2o, h2o_cmd, h2o_hosts
import h2o_browse as h2b
import h2o_import as h2i

class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        # assume we're at 0xdata with it's hdfs namenode
        global localhost
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(1)
        else:
            # all hdfs info is done thru the hdfs_config michal's ec2 config sets up?
            h2o_hosts.build_cloud_with_hosts(1, 
            # this is for our amazon ec hdfs
            # see https://github.com/0xdata/h2o/wiki/H2O-and-s3n
            hdfs_name_node='10.78.14.235:9000',
            hdfs_version='0.20.2')

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_parse_covtype20x_s3n_thru_hdfs(self):
        csvFilename = "covtype20x.data"
        trialMax = 3
        timeoutSecs = 500
        URI = "s3n://home-0xdiag-datasets"
        s3nKey = URI + "/" + csvFilename

        for trial in range(trialMax):
            # since we delete the key, we have to re-import every iteration
            # s3n URI thru HDFS is not typical.
            importHDFSResult = h2o.nodes[0].import_hdfs(URI)
            s3nFullList = importHDFSResult['succeeded']
            ### print "s3nFullList:", h2o.dump_json(s3nFullList)
            self.assertGreater(len(s3nFullList),1,"Didn't see more than 1 files in s3n?")

            key2 = csvFilename + "_" + str(trial) + ".hex"
            print "Loading s3n key: ", s3nKey, 'thru HDFS'
            start = time.time()
            parseResult = h2o.nodes[0].parse(s3nKey, key2,
                timeoutSecs=500, retryDelaySecs=10, pollTimeoutSecs=60)
            elapsed = time.time() - start

            print s3nKey, 'parse time:', parseResult['response']['time']
            print "parse result:", parseResult['destination_key']
            print "Trial #", trial, "completed in", elapsed, "seconds.", \
                "%d pct. of timeout" % ((elapsed*100)/timeoutSecs)

            print "Deleting key in H2O so we get it from S3 (if ec2) or nfs again.", \
                  "Otherwise it would just parse the cached key."
            storeView = h2o.nodes[0].store_view()
            ### print "storeView:", h2o.dump_json(storeView)
            # h2o removes key after parse now
            ### print "Removing", s3nKey
            ### removeKeyResult = h2o.nodes[0].remove_key(key=s3nKey)
            ### print "removeKeyResult:", h2o.dump_json(removeKeyResult)


if __name__ == '__main__':
    h2o.unit_main()
