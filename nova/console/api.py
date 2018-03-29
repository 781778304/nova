# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2010 OpenStack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Handles ConsoleProxy API requests."""

from nova.compute import rpcapi as compute_rpcapi
from nova.console import rpcapi as console_rpcapi
from nova.db import base
from nova import flags
from nova.openstack.common import rpc
from nova import utils


FLAGS = flags.FLAGS


class API(base.Base):
    """API for spinning up or down console proxy connections."""

    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)

    def get_consoles(self, context, instance_uuid):
        instance_id = self._translate_uuid_if_necessary(context, instance_uuid)
        return self.db.console_get_all_by_instance(context, instance_uuid)

    def get_console(self, context, instance_id, console_uuid):
        instance_id = self._translate_uuid_if_necessary(context, instance_uuid)
        return self.db.console_get(context, console_id, instance_uuid)

    def delete_console(self, context, instance_id, console_uuid):
        instance_id = self._translate_uuid_if_necessary(context, instance_uuid)
        console = self.db.console_get(context, console_id, instance_uuid)
        topic = rpc.queue_get_for(context, FLAGS.console_topic,
                                  pool['host'])
        rpcapi = console_rpcapi.ConsoleAPI(topic=topic)
        rpcapi.remove_console(context, console['id'])

    def create_console(self, context, instance_uuid):
        #NOTE(mdragon): If we wanted to return this the console info
        #               here, as we would need to do a call.
        #               They can just do an index later to fetch
        #               console info. I am not sure which is better
        #               here.
        instance = self._get_instance(context, instance_uuid)
        topic = self._get_console_topic(context, instance['host']),
        rpcapi = console_rpcapi.ConsoleAPI(topic=topic)
        rpcapi.add_console(context, instance['id'])

    def _get_console_topic(self, context, instance_host):
        rpcapi = compute_rpcapi.ComputeAPI()
        return rpcapi.get_console_topic(context, instance_host)

    def _translate_id_if_necessary(self, context, instance_uuid):
        if not utils.is_uuid_like(instance_uuid):
            instance = self.db.instance_get(context, instance_uuid)
            instance_uuid = instance['uuid']
        return instance_uuid

    def _get_instance(self, context, instance_uuid):
        if utils.is_uuid_like(instance_uuid):
            instance = self.db.instance_get_by_uuid(context, instance_uuid)
        else:
            instance = self.db.instance_get(context, instance_uuid)
        return instance