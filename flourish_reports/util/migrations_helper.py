import pytz
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder
from datetime import datetime


class MigrationHelper:

    connection = connections[DEFAULT_DB_ALIAS]
    loader = MigrationLoader(connection)
    graph = loader.graph

    def __init__(self, app_name: str, model_name: str) -> None:
        self.tz = pytz.timezone('Africa/Gaborone')
        self.app_name = app_name
        self.model_name = model_name

    def get_model_creation_date(self):
        for key in self.graph.nodes:
            migration = self.loader.get_migration(*key)
            if migration.app_label == self.app_name:
                for operation in migration.operations:
                    if (operation.__class__.__name__ == 'CreateModel' and
                            operation.name.lower() == self.model_name.lower()):
                        recorder = MigrationRecorder.Migration.objects.filter(
                            app=self.app_name, name=migration.name).first()
                        if recorder:
                            dt_applied = recorder.applied.astimezone(self.tz)
                            return dt_applied.date()

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
                        record = {
                            'date_applied': dt_applied.isoformat(),
                            'operation_applied': operation.describe(),
                            'model': f'{self.app_name}.{model_name.lower()}',
                            'operation_type': operation_type, }
                        self.records.append(record)

    def get_date_created(self, model_name):

        result = list(filter(lambda r: r['model'] == model_name, self.records))

        if result:
            result = result[0]
            return datetime.fromisoformat(result['date_applied']).date()
