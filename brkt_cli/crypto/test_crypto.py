# Copyright 2015 Bracket Computing, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
# https://github.com/brkt/brkt-cli/blob/master/LICENSE
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and
# limitations under the License.
import unittest

import brkt_cli.crypto
from cryptography.hazmat.backends.openssl import ec

# These PEMs were generated by openssl, and must only be used for
# unit testing.
TEST_PRIVATE_KEY_PEM = """-----BEGIN EC PRIVATE KEY-----
MIGkAgEBBDBw1jk43okFLLLad4OgdsSIwsUdJ3BzxzuZWM/bBpF+GKJ7D9hJd3W7
TBKMrozqEqOgBwYFK4EEACKhZANiAASbklkQuPGQTJL37dGI0TYoSFQ8aFdogUzV
9XdUz3s5z9CDGmIuIjB+gNPplCyWJzrENC5v+ao4TLee1ZyXsnDCP25Za0UiPuU+
IpuqIVEKCSDTG96q2bCqDIT45qjOWBQ=
-----END EC PRIVATE KEY-----
"""
TEST_PRIVATE_KEY_X = int(
    '23944671740498376501544907634910018068896593728651488954476245338720275'
    '820003446148266017687349159128610913381656378'
)
TEST_PRIVATE_KEY_Y = int(
    '30198533853195572636850285556018792732205254449690882000990730634871805'
    '883491943919079902332284216113666861239785492'
)

TEST_ENCRYPTED_PRIVATE_KEY_PEM = """-----BEGIN EC PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-256-CBC,35BACC9F9023D5206DEC871E734B139B

TEOwSpTBoOPpwQU8u7SJaJqSIUwk6SfHZkXs205xoELtHbNcWV1vr0/DsQ1B2b3c
ZIO1bvHQOKl3X76hUxqzSBSx7kFqN2igjXGaQ2SmkZrzqhqAEo7YScpMQQgvk15B
U7wZaJcaN6RelbwRqnM7Qk9HqD5U9+lvS7g7vhP++AXhQretG7l9LYMZKxk3F/th
pZPjFPt2fjlVkJnhl6NkhsTder9rJE3qKlP9JM8zwUQ=
-----END EC PRIVATE KEY-----"""
TEST_ENCRYPTED_PRIVATE_KEY_PASSWORD = 'test123'


class TestCrypto(unittest.TestCase):

    def test_from_pem(self):
        def _check_fields(crypto):
            self.assertEqual(brkt_cli.crypto.SECP384R1, crypto.curve)
            self.assertEqual(TEST_PRIVATE_KEY_X, crypto.x)
            self.assertEqual(TEST_PRIVATE_KEY_Y, crypto.y)

        # Unencrypted private key.
        crypto = brkt_cli.crypto.from_private_key_pem(TEST_PRIVATE_KEY_PEM)
        _check_fields(crypto)

        # Encrypted private key.
        crypto = brkt_cli.crypto.from_private_key_pem(
            TEST_ENCRYPTED_PRIVATE_KEY_PEM,
            TEST_ENCRYPTED_PRIVATE_KEY_PASSWORD
        )
        _check_fields(crypto)

    def test_invalid_pem(self):
        with self.assertRaises(ValueError):
            brkt_cli.crypto.from_private_key_pem('foobar')

    def test_is_encrypted_key(self):
        self.assertTrue(
            brkt_cli.crypto.is_encrypted_key(TEST_ENCRYPTED_PRIVATE_KEY_PEM))
        self.assertFalse(
            brkt_cli.crypto.is_encrypted_key(TEST_PRIVATE_KEY_PEM)
        )

    def test_is_private_key(self):
        public_pem = TEST_PRIVATE_KEY_PEM.replace('PRIVATE', 'PUBLIC')
        self.assertTrue(brkt_cli.crypto.is_private_key(TEST_PRIVATE_KEY_PEM))
        self.assertFalse(brkt_cli.crypto.is_private_key(public_pem))
        self.assertFalse(brkt_cli.crypto.is_private_key('xyz'))

    def test_generate(self):
        """ Test generating a key pair.
        """
        crypto = brkt_cli.crypto.new()
        self.assertTrue(
            isinstance(crypto.private_key, ec._EllipticCurvePrivateKey))
        self.assertTrue(
            isinstance(crypto.public_key, ec._EllipticCurvePublicKey))
        self.assertTrue('BEGIN PUBLIC KEY' in crypto.public_key_pem)

        pem = crypto.get_private_key_pem()
        self.assertTrue('BEGIN EC PRIVATE KEY' in pem)
        pem = crypto.get_private_key_pem('test123')
        self.assertTrue('Proc-Type: 4,ENCRYPTED' in pem)
