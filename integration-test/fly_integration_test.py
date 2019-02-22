import unittest


from concourse_search.fly import (
    FlyViaHttp,
    FlyBuildNotFound,
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

        watch_response = fly.watch('gpdb-prod', 'gpdb_master', 'icw_planner_centos6', 1551)

        lines = watch_response.lines()
        
        self.assertIn('checking for stdint.h... ', lines)

    def test_it_returns_failed_builds(self):
        fly = FlyViaHttp()

        watch_response = fly.watch('gpdb-prod', 'gpdb_master', 'icw_planner_centos6', 9)

        self.assertFalse(watch_response.was_success())
        
    def test_it_throws_an_exception_when_asking_for_a_job_that_does_not_exist(self):
        fly = FlyViaHttp()

        with self.assertRaises(FlyBuildNotFound):
            fly.watch('gpdb-prod', 'gpdb-master', 'some-nonsense', 1)
