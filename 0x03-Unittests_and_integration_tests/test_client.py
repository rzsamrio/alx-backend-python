#!/usr/bin/env python3
"""Tests for client.py."""
from unittest import TestCase
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(TestCase):
    """Tests for the Github client."""

    @parameterized.expand([
        ("google"),
        ("abc"),
    ])
    def test_org(self, org):
        """Test the org property."""
        with patch("client.get_json", return_value="Response") as get:
            github_client = GithubOrgClient(org)
            self.assertEqual(github_client.org, "Response")
            self.assertEqual(github_client.org, "Response")
            get.assert_called_once_with(github_client.ORG_URL.format(org=org))

    @parameterized.expand([
        (["http://A", "http://B", "http://C"],),
        (["http://qwdq.wq", "http://adfsf"],),
        ([],),
    ])
    def test_public_repos_url(self, repos):
        """Test the public_repos_url property"""
        github_client = GithubOrgClient("google")
        fake_org = {
            "repos_url": repos,
        }
        with patch.object(GithubOrgClient, "org",
                          new_callable=PropertyMock) as fake:
            fake.return_value = fake_org
            self.assertEqual(github_client._public_repos_url,
                             fake_org["repos_url"])

    @patch(
        "client.get_json",
        return_value=[
            {
                "name": "Test Repo",
                "license": {"key": "test"},
            },
        ]
    )
    def test_public_repos(self, get_json):
        """Test the public_repos property."""
        with patch.object(GithubOrgClient,
                          "_public_repos_url",
                          new_callable=PropertyMock) as public_repos_url:
            public_repos_url.return_value = "https://some.random.url"
            github_client = GithubOrgClient("google")
            self.assertEqual(github_client.public_repos(),
                             ["Test Repo"])
            public_repos_url.assert_called_once()
            get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, key, contained):
        """Test the has_license method."""
        self.assertEqual(GithubOrgClient.has_license(repo, key), contained)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(TestCase):
    """Integration tests for the Github client."""

    @classmethod
    def setUpClass(self):
        """Setup a mocking of requests.get."""
        def requester(url):
            """Return the test data for a particular url."""
            response = Mock()
            if url == self.org_payload.get("repos_url"):
                response.json.return_value = self.repos_payload
            else:
                response.json.return_value = self.org_payload
            return response

        patcher = patch("requests.get", side_effect=requester)
        self.get_patcher = patcher.start()

    def test_public_repos(self):
        """Test that the correct public repos are returned."""
        github_client = GithubOrgClient("google")
        self.assertEqual(github_client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test that the correct public repos are returned."""
        github_client = GithubOrgClient("google")
        self.assertEqual(github_client.public_repos(license="apache-2.0"),
                         self.apache2_repos)

    @classmethod
    def tearDownClass(self):
        """Stop the mock of requests.get."""
        self.get_patcher.stop()
