import uuid
from datetime import datetime

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from models import Slot, Qualification, Operator, Sector, Constraint, Availability

DATE_FORMAT = '%d/%m/%YT%H:%M'

# Replace 'path/to/credentials.json' with your service account credentials file
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json')
client = gspread.authorize(creds)

# Open the specific Google Sheet by its URL or title
sheet = client.open_by_url(
    'https://docs.google.com/spreadsheets/d/1AG_Sy363wFnZA-0y1oOpmOKaIff7TKP61sLIGzMhXng/edit?usp=sharing')
# or: sheet = client.open('Your Sheet Title')

# Get data from a specific worksheet
worksheet = sheet.worksheets()
operators_ws = [ws for ws in worksheet if ws.title == 'operators'][0]
shifts_ws = [ws for ws in worksheet if ws.title == 'shifts'][0]
requests_ws = [ws for ws in worksheet if ws.title == 'requests'][0]
constraints_ws = [ws for ws in worksheet if ws.title == 'constraints'][0]


def load_slots():
    shifts = []
    shifts_df = pd.DataFrame(shifts_ws.get_all_records())
    for row in shifts_df.to_dict(orient='records'):
        shifts.append(Slot(
            id=uuid.uuid4(),
            start_time=datetime.strptime(f'{row["start_date"]}T{row["start_time"]}', DATE_FORMAT),
            end_time=datetime.strptime(f'{row["end_date"]}T{row["end_time"]}', DATE_FORMAT),
            qualification=Qualification(row['qualification']),
            description=row['description'],
            pre_scheduled=row['pre_scheduled'],
        ))
    return shifts

    # shifts_to_place = []
    # start_date = datetime(2023, 12, 3, 6)
    # for day in range(3):
    #     for hour in range(0, 24, 4):
    #         for i in range(2):
    #             shifts_to_place.append(Shift(
    #                 id=uuid.uuid4(),
    #                 start_time=start_date + pd.Timedelta(f'{day} days {hour} hours'),
    #                 end_time=start_date + pd.Timedelta(f'{day} days {hour + 4} hours'),
    #                 qualification=Qualification.TOL_OPERATOR,
    #             ))
    #             shifts_to_place.append(Shift(
    #                 id=uuid.uuid4(),
    #                 start_time=start_date + pd.Timedelta(f'{day} days {hour} hours'),
    #                 end_time=start_date + pd.Timedelta(f'{day} days {hour + 4} hours'),
    #                 qualification=Qualification.TOL_COMMANDEER,
    #             ))
    #         for i in range(2):
    #             shifts_to_place.append(Shift(
    #                 id=uuid.uuid4(),
    #                 start_time=start_date + pd.Timedelta(f'{day} days {hour} hours'),
    #                 end_time=start_date + pd.Timedelta(f'{day} days {hour + 4} hours'),
    #                 qualification=Qualification.HEAVY_OPERATOR,
    #             ))
    #             shifts_to_place.append(Shift(
    #                 id=uuid.uuid4(),
    #                 start_time=start_date + pd.Timedelta(f'{day} days {hour} hours'),
    #                 end_time=start_date + pd.Timedelta(f'{day} days {hour + 4} hours'),
    #                 qualification=Qualification.HEAVY_COMMANDEER,
    #             ))
    #         for i in range(3):
    #             shifts_to_place.append(Shift(
    #                 id=uuid.uuid4(),
    #                 start_time=start_date + pd.Timedelta(f'{day} days {hour} hours'),
    #                 end_time=start_date + pd.Timedelta(f'{day} days {hour + 4} hours'),
    #                 qualification=Qualification.SIUA_OPERATOR,
    #             ))
    #             shifts_to_place.append(Shift(
    #                 id=uuid.uuid4(),
    #                 start_time=start_date + pd.Timedelta(f'{day} days {hour} hours'),
    #                 end_time=start_date + pd.Timedelta(f'{day} days {hour + 4} hours'),
    #                 qualification=Qualification.SIUA_COMMANDER,
    #             ))
    #             shifts_to_place.append(Shift(
    #                 id=uuid.uuid4(),
    #                 start_time=start_date + pd.Timedelta(f'{day} days {hour} hours'),
    #                 end_time=start_date + pd.Timedelta(f'{day} days {hour + 4} hours'),
    #                 qualification=Qualification.SIUA_SHLISHI,
    #             ))
    # return shifts_to_place


def load_operators() -> list[Operator]:
    opeartors_df = pd.DataFrame(operators_ws.get_all_records())
    operators = []
    for row in opeartors_df.to_dict(orient='records'):
        operator = Operator(
            id=row['id'],
            name=row['name'],
            sector=Sector(row['sector']),
            availabilities=[Availability(
                start=datetime(2022, 5, 1, 0, 0, 0),
                end=datetime(2024, 5, 7, 0, 0, 0),
            )]
        )
        [operator.qualifications.append(qualification) if row[qualification.value] else None
         for qualification in Qualification]
        operators.append(operator)
        operator.auto_slot = False if row['auto_shift'] == 0 else True
    constraints_df = pd.DataFrame(constraints_ws.get_all_records())
    for row in constraints_df.to_dict(orient='records'):
        operator = next(operator for operator in operators if operator.name == row['operator'])
        operator.constraints.append(Constraint(
            description=row['description'],
            start=datetime.strptime(f'{row["start_date"]}T{row["start_time"]}', DATE_FORMAT),
            end=datetime.strptime(f'{row["end_date"]}T{row["end_time"]}', DATE_FORMAT),
        ))
    return operators

    # operators = [
    #     Operator(
    #         id=1,
    #         name="Alice",
    #         qualifications=[Qualification.TOL_COMMANDEER, Qualification.HEAVY_COMMANDEER],
    #         requests=[
    #             Request(
    #                 start=datetime(2023, 5, 1, 0, 0, 0),
    #                 end=datetime(2023, 5, 1, 10, 59, 59),
    #                 description="Dentist",
    #                 score=80
    #             ),
    #             Request(
    #                 start=datetime(2023, 5, 4, 18, 0, 0),
    #                 end=datetime(2023, 5, 5, 10, 0, 0),
    #                 description="Birthday",
    #                 score=20
    #             )
    #         ],
    #         group=Group.MARATHON,
    #     ),
    #     Operator(
    #         id=2,
    #         name="Bob",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR],
    #         requests=[
    #             Request(
    #                 start=datetime(2023, 5, 3, 0, 0, 0),
    #                 end=datetime(2023, 5, 3, 10, 59, 59),
    #                 description="Dentist",
    #                 score=80
    #             ),
    #             Request(
    #                 start=datetime(2023, 5, 6, 10, 0, 0),
    #                 end=datetime(2023, 5, 6, 18, 0, 0),
    #                 description="Birthday",
    #                 score=20
    #             )
    #         ],
    #         group=Group.MARATHON,
    #     ),
    #     Operator(
    #         id=3,
    #         name="Charlie",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #         requests=[
    #             Request(
    #                 start=datetime(2023, 5, 3, 18, 0, 0),
    #                 end=datetime(2023, 5, 3, 22, 59, 59),
    #                 description="Dentist",
    #                 score=80
    #             ),
    #             Request(
    #                 start=datetime(2023, 5, 2, 18, 0, 0),
    #                 end=datetime(2023, 5, 3, 10, 0, 0),
    #                 description="Birthday",
    #                 score=20
    #             )
    #         ],
    #         group=Group.MARATHON,
    #     ),
    #     Operator(
    #         id=4,
    #         name="Dave",
    #         qualifications=[Qualification.TOL_OPERATOR],
    #     ),
    #     Operator(
    #         id=5,
    #         name="Eve",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #     ),
    #     Operator(
    #         id=6,
    #         name="Frank",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #     ),
    #     Operator(
    #         id=7,
    #         name="Grace",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #     ),
    #     Operator(
    #         id=8,
    #         name="Hank",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #     ),
    #     Operator(
    #         id=9,
    #         name="Ivy",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #     ),
    #     Operator(
    #         id=10,
    #         name="Judy",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #     ),
    #     Operator(
    #         id=11,
    #         name="Kevin",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #     ),
    #     Operator(
    #         id=12,
    #         name="Linda",
    #         qualifications=[Qualification.TOL_OPERATOR, Qualification.HEAVY_OPERATOR, Qualification.TOL_COMMANDEER,
    #                         Qualification.HEAVY_COMMANDEER],
    #     ),
    # ]
    # return operators
