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

import argparse


def setup_encrypt_ami_args(parser):
    parser.add_argument(
        'ami',
        metavar='ID',
        help='The guest AMI that will be encrypted'
    )
    parser.add_argument(
        '--encrypted-ami-name',
        metavar='NAME',
        dest='encrypted_ami_name',
        help='Specify the name of the generated encrypted AMI',
        required=False
    )
    parser.add_argument(
        '--guest-instance-type',
        metavar='TYPE',
        dest='guest_instance_type',
        help=(
            'The instance type to use when running the unencrypted guest '
            'instance'),
        default='m3.medium'
    )
    parser.add_argument(
        '--hvm',
        action='store_true',
        help='Use the HVM encryptor',
        dest='hvm'
    )
    parser.add_argument(
        '--no-validate',
        dest='validate',
        action='store_false',
        default=True,
        help="Don't validate AMIs, subnet, and security groups"
    )
    parser.add_argument(
        '--ntp-server',
        metavar='DNS Name',
        dest='ntp_servers',
        action='append',
        help=(
            'Optional NTP server to sync Metavisor clock. '
            'May be specified multiple times.'
        )
    )

    proxy_group = parser.add_mutually_exclusive_group()
    proxy_group.add_argument(
        '--proxy',
        metavar='HOST:PORT',
        help=(
            'Use this HTTPS proxy during encryption.  '
            'May be specified multiple times.'
        ),
        dest='proxies',
        action='append'
    )
    proxy_group.add_argument(
        '--proxy-config-file',
        metavar='PATH',
        help='Path to proxy.yaml file that will be used during encryption',
        dest='proxy_config_file'
    )

    parser.add_argument(
        '--region',
        metavar='NAME',
        help='AWS region (e.g. us-west-2)',
        dest='region',
        required=True
    )
    parser.add_argument(
        '--security-group',
        metavar='ID',
        dest='security_group_ids',
        action='append',
        help=(
            'Use this security group when running the encryptor instance. '
            'May be specified multiple times.'
        )
    )
    parser.add_argument(
        '--subnet',
        metavar='ID',
        dest='subnet_id',
        help='Launch instances in this subnet'
    )
    parser.add_argument(
        '--tag',
        metavar='KEY=VALUE',
        dest='tags',
        action='append',
        help=(
            'Custom tag for resources created during encryption. '
            'May be specified multiple times.'
        )
    )
    parser.add_argument(
        '-v',
        '--verbose',
        dest='encrypt_ami_verbose',
        action='store_true',
        help='Print status information to the console'
    )

    # Optional yeti endpoints. Hidden because it's only used for development.
    # If you're using this option, it should be passed as a comma separated
    # list of endpoints. ie blb.*.*.brkt.net:7002,blb.*.*.brkt.net:7001 the
    # endpoints must also be in order: api_host,hsmproxy_host
    parser.add_argument(
        '--brkt-env',
        dest='brkt_env',
        help=argparse.SUPPRESS
    )

    # Optional AMI ID that's used to launch the encryptor instance.  This
    # argument is hidden because it's only used for development.
    parser.add_argument(
        '--encryptor-ami',
        metavar='ID',
        dest='encryptor_ami',
        help=argparse.SUPPRESS
    )

    # Optional EC2 SSH key pair name to use for launching the guest
    # and encryptor instances.  This argument is hidden because it's only
    # used for development.
    parser.add_argument(
        '--key',
        metavar='NAME',
        help=argparse.SUPPRESS,
        dest='key_name'
    )

    # This option is still in development.
    """
    help=(
        'JSON Web Token that the encrypted instance will use to '
        'authenticate with the Bracket service.  Use the make-jwt '
        'subcommand to generate a JWT.'
    )
    """
    parser.add_argument(
        '--jwt',
        help=argparse.SUPPRESS
    )
