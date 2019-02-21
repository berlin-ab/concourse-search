import unittest


from concourse_search.fly import (
    FlyViaHttp,
)


class FlyViaHttpIntegrationTest(unittest.TestCase):
    def test_it_can_load_targets(self):
        fly = FlyViaHttp()

        urls = [target.url() for target in fly.targets()]
        
        self.assertIn('https://dev.ci.gpdb.pivotal.io', urls)

    def test_it_can_find_a_matching_target(self):
        fly = FlyViaHttp()

        target = fly.target_matching('gpdb-dev')
                
        self.assertEqual('https://dev.ci.gpdb.pivotal.io', target.url())

    def test_it_returns_raw_concourse_build_output(self):
        fly = FlyViaHttp()
        # curl -H "Authorization: Bearer $BEARER_TOKEN" https://prod.ci.gpdb.pivotal.io/api/v1/teams/main/pipelines/gpdb_master/jobs/icw_planner_centos6/builds/2
        # gives the build url, where you can get the events
        # curl -H "Authorization: Bearer $BEARER_TOKEN" https://prod.ci.gpdb.pivotal.io/api/v1/builds/886/events


        watch_response = fly.watch('gpdb-prod', 'gpdb_master', 'icw_planner_centos6', 1551)

        raw_lines = watch_response.raw_lines()
        
        self.assertIn('checking for stdint.h... yes', raw_lines)
        
