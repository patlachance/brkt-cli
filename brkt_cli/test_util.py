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
import tempfile
import unittest
import time

from brkt_cli import parse_brkt_env, util
from brkt_cli.crypto import test_crypto
from brkt_cli.validation import ValidationError


class TestUtil(unittest.TestCase):

    def test_append_suffix(self):
        """ Test that we append the suffix and truncate the original name.
        """
        name = 'Boogie nights are always the best in town'
        suffix = ' (except Tuesday)'
        encrypted_name = util.append_suffix(
            name, suffix, max_length=128)
        self.assertTrue(encrypted_name.startswith(name))
        self.assertTrue(encrypted_name.endswith(suffix))

        # Make sure we truncate the original name when it's too long.
        name += ('X' * 100)
        encrypted_name = util.append_suffix(
            name, suffix, max_length=128)
        self.assertEqual(128, len(encrypted_name))
        self.assertTrue(encrypted_name.startswith('Boogie nights'))

    def test_parse_name_value(self):
        self.assertEqual(
            ('foo', 'bar'),
            util.parse_name_value('foo=bar')
        )
        with self.assertRaises(ValidationError):
            util.parse_name_value('abc')


class TestBase64(unittest.TestCase):
    """ Test that our encoding code follows the spec used by JWT.  The
    encoded string must be URL-safe and not use padding. """

    def test_encode_and_decode(self):
        for length in xrange(0, 1000):
            content = 'x' * length
            encoded = util.urlsafe_b64encode(content)
            self.assertFalse('/' in encoded)
            self.assertFalse('_' in encoded)
            self.assertFalse('=' in encoded)
            self.assertEqual(
                content, util.urlsafe_b64decode(encoded))


class TestException(Exception):
    pass


class TestUnexpectedException(Exception):
    pass


class TestRetryExceptionChecker(util.RetryExceptionChecker):

    def is_expected(self, exception):
        return isinstance(exception, TestException)


class TestRetry(unittest.TestCase):

    def setUp(self):
        self.num_calls = 0

    def _fail_for_n_calls(self, n, sleep_time=0,
                          exception_class=TestException):
        self.num_calls += 1
        time.sleep(sleep_time)
        if self.num_calls <= n:
            raise exception_class()

    def _get_wrapped(self, timeout=1.0, on=None, use_exception_checker=True):
        checker = None
        if use_exception_checker:
            checker = TestRetryExceptionChecker()
        return util.retry(
            self._fail_for_n_calls,
            on=on,
            exception_checker=checker,
            initial_sleep_seconds=0,
            timeout=timeout
        )

    def test_five_failures(self):
        """ Test that we handle failing 5 times and succeeding the 6th
        time.
        """
        self._get_wrapped()(5)
        self.assertEqual(6, self.num_calls)

    def test_timeout(self):
        """ Test that we raise the underlying exception when the timeout
        has been exceeded.
        """
        with self.assertRaises(TestException):
            self._get_wrapped(timeout=0.05)(10, sleep_time=0.02)

    def test_unexpected_exception(self):
        """ Test that we raise the underlying exception when it's not
        one of the expected exception types.
        """
        with self.assertRaises(TestUnexpectedException):
            self._get_wrapped()(5, exception_class=TestUnexpectedException)
        self.assertEqual(1, self.num_calls)

    def test_on(self):
        """ Test retry based on the exception type. """
        self._get_wrapped(on=[TestException])(5)
        self.assertEqual(6, self.num_calls)


# This PEM was generated by openssl, and must only be used for
# unit testing.
TEST_SECT163K1_PRIVATE_KEY_PEM = """-----BEGIN EC PRIVATE KEY-----
MFMCAQEEFQGZdbOd9KrGmynCqcy3S1QDvq67xqAHBgUrgQQAAaEuAywABAej5bYZ
ZN4/1PqYAE8Cz4aSMC8KjgCDfMkzv0VURQGcSQ5xc4aCnI7bIQ==
-----END EC PRIVATE KEY-----
"""


class TestReadPrivateKey(unittest.TestCase):

    def test_read_private_key(self):
        """ Test reading the signing key from a file. """
        # Write private key to a temp file.
        key_file = tempfile.NamedTemporaryFile()
        key_file.write(test_crypto.TEST_PRIVATE_KEY_PEM)
        key_file.flush()

        crypto = util.read_private_key(key_file.name)
        self.assertEqual(
            test_crypto.TEST_PRIVATE_KEY_X, crypto.x)
        key_file.close()

    def test_read_private_key_invalid_curve(self):
        """ Test that we require NIST384p for the signing key. """
        # Write private key to a temp file.
        key_file = tempfile.NamedTemporaryFile()
        key_file.write(TEST_SECT163K1_PRIVATE_KEY_PEM)
        key_file.flush()

        with self.assertRaises(ValidationError):
            util.read_private_key(key_file.name)
        key_file.close()

    def test_read_private_key_io_error(self):
        """ Test that we handle IOError when reading the signing key.
        """
        # Read from a directory.
        with self.assertRaises(ValidationError):
            util.read_private_key('.')

        # Read from a file that doesn't exist.
        with self.assertRaises(ValidationError):
            util.read_private_key('nothing_here.pem')

        # Read from a malformed file.
        key_file = tempfile.NamedTemporaryFile()
        key_file.write('abc')
        key_file.flush()

        with self.assertRaises(ValidationError):
            util.read_private_key(key_file.name)
        key_file.close()
