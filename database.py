from peewee import *
import datetime

sqlite_db = SqliteDatabase('/home/travail/Python/trading/database.db', pragmas={'journal_mode': 'wal'})
#sqlite_db = MySQLDatabase("chaufeau", host="127.0.0.1", port=3306, user="root", passwd="ng92garxr")

# Connect to a Postgres database.
#sqlite_db = PostgresqlDatabase('chaufeau', user='chaufeau', password='chaufeau', host='127.0.0.1', port=5432)

class logs_database(Model):
    currency = CharField()
    value = FloatField(null=True)
    date = DateTimeField(default=datetime.datetime.now())

    def save(self, *args, **kwargs):
        self.date = datetime.datetime.now()
        super(logs_database, self).save(*args, **kwargs)

    class Meta:
        database = sqlite_db
        db_table = 'logs_database'


if sqlite_db.is_closed() == True:
    dates = datetime.datetime.now()

# if dates.hour == 0 and dates.minute == 0:
# sqlite_db.drop_tables([logs_database], safe=True)
logs_database.create_table()
