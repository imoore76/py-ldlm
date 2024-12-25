# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from grpc import Channel, ChannelCredentials
import pytest
from unittest import mock

from ldlm.base_client import (
    readfile,
    BaseClient,
    TLSConfig,
)


class MockedClient(BaseClient):

    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the class.
        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        This method initializes the `_create_channel` attribute of the object with a MagicMock object.
        It then calls the `__init__` method of the parent class with the given arguments.

        """
        self._create_channel = mock.MagicMock()
        super().__init__(*args, **kwargs)

    _create_channel = None


class TestTLSConfig:

    @pytest.fixture(autouse=True)
    def mock_stub(self):
        """
        Don't make extra calls to the mocked channel that we want to assert calls for
        """
        with mock.patch("ldlm.base_client.ldlm_grpc.LDLMStub"):
            yield

    @pytest.fixture
    def mock_creds(self):
        with mock.patch("ldlm.base_client.grpc.ssl_channel_credentials") as m:
            yield m

    def test_no_ssl_config(self, mock_creds):
        """
        Test that when no tls config is provided, the _create_channel method is called with the
        correct arguments (address, None).
        """
        c = MockedClient("ldlm-server:3144")

        assert mock_creds.mock_calls == []
        assert c._create_channel.mock_calls == [
            mock.call("ldlm-server:3144", None),
        ]

    def test_empty_ssl_config(self, mock_creds):
        """
        Test that when all certificates are provided, ssl_channel_credentials method is called with
        the correct values (None, None, None), and that the resulting object is passed to the
        _create_channel method.
        """
        tls = TLSConfig()
        c = MockedClient("ldlm-server:3144", tls=tls)

        assert mock_creds.mock_calls == [
            mock.call(
                root_certificates=None,
                private_key=None,
                certificate_chain=None,
            )
        ]
        print(c._create_channel.mock_calls)
        assert c._create_channel.mock_calls == [
            mock.call("ldlm-server:3144", mock_creds.return_value),
        ]

    def test_all_certs(self, mock_creds):
        """
        Test that when all certificates are provided, ssl_channel_credentials method is called with
        the correct values, and that the resulting object is passed to the _create_channel method.
        """
        tls = TLSConfig(
            ca_file="tests/certs/ca_cert.pem",
            cert_file="tests/certs/client_cert.pem",
            key_file="tests/certs/client_key.pem",
        )
        c = MockedClient("ldlm-server:3144", tls=tls)

        assert mock_creds.mock_calls == [
            mock.call(
                root_certificates=readfile("tests/certs/ca_cert.pem"),
                private_key=readfile("tests/certs/client_key.pem"),
                certificate_chain=readfile("tests/certs/client_cert.pem"),
            )
        ]
        assert c._create_channel.mock_calls == [
            mock.call("ldlm-server:3144", mock_creds.return_value),
        ]
