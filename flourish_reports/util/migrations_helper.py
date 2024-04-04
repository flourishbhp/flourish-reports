import os
import sys
import pytz
import pandas as pd
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder
from django.db import DEFAULT_DB_ALIAS, connections
from datetime import datetime

class MigrationHelper:

    connection = connections[DEFAULT_DB_ALIAS]
    loader = MigrationLoader(connection)

    def __init__(self, app_name: str) -> None:
        self.records = []
        self.migrations = MigrationRecorder.Migration.objects.filter(app__startswith=app_name)
        self.tz = pytz.timezone('Africa/Gaborone')
        self.app_name = app_name
        self.bootsrap()

    def bootsrap(self):
        for migration in self.migrations:
            try:
                operations = self.loader.get_migration_by_prefix(
                    migration.app, migration.name).operations
            except KeyError:
                continue
            else:
                for operation in operations:
                    operation_type, _, details = operation.deconstruct()
                    dt_applied = migration.applied.astimezone(self.tz)

                    model_name = details.get('name', None)

                    if model_name:
                        record = {'date_applied': dt_applied.isoformat(),
                                'operation_applied': operation.describe(),
                                'model': f"{self.app_name}.{model_name.lower()}",
                                'operation_type': operation_type, }
                        self.records.append(record)

    def get_date_created(self, model_name):

        result = list(filter(lambda r: r['model'] == model_name, self.records))

        if result:
            result = result[0]            
            return datetime.fromisoformat(result['date_applied']).date()
