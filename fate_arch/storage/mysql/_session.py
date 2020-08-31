#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import pymysql

from fate_arch.abc import AddressABC
from fate_arch.common.address import MysqlAddress
from fate_arch.common.profile import log_elapsed
from fate_arch.storage import StorageSessionBase, MySQLStorageType


class StorageSession(StorageSessionBase):
    def __init__(self, session_id, options=None):
        super(StorageSession, self).__init__(session_id=session_id)
        self.con = None
        self.cur = None
        self.address = None

    def create(self):
        pass

    def table(self, name, namespace, address: AddressABC, partitions, storage_type: MySQLStorageType = MySQLStorageType.InnoDB, options=None, **kwargs):
        self.address = address
        if isinstance(address, MysqlAddress):
            from fate_arch.storage.mysql._table import StorageTable
            self.create_db()
            self.con = pymysql.connect(host=address.host,
                                       user=address.user,
                                       passwd=address.passwd,
                                       port=address.port,
                                       db=address.db)
            self.cur = self.con.cursor()
            return StorageTable(cur=self.cur, con=self.con, address=address, name=name, namespace=namespace, storage_type=storage_type, partitions=partitions, options=options)
        raise NotImplementedError(f"address type {type(address)} not supported with eggroll storage")

    @log_elapsed
    def cleanup(self, name, namespace):
        pass

    @log_elapsed
    def stop(self):
        return self.con.close()

    @log_elapsed
    def kill(self):
        return self.con.close()

    def create_db(self):
        conn = pymysql.connect(host=self.address.host,
                               user=self.address.user,
                               password=self.address.passwd,
                               port=self.address.port)
        cursor = conn.cursor()
        cursor.execute("create database if not exists {}".format(self.address.db))
        print('create db {} success'.format(self.address.db))
        conn.close()
