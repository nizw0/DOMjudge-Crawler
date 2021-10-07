import base64
import json
import os
from zipfile import ZipFile

import requests

from config import account, password, url


auth = account, password


class FailToCatchContestError(Exception):
    def __init__(self):
        super(Exception, self).__init__()

    def __str__(self):
        return '找不到這個contest，請重新輸入'


def decode_json(x):
    return json.loads(x.text)


def download_submission_by_cid(contest_id):
    judgements = requests.get(f'{url}/contests/{contest_id}/judgements', auth=auth)
    if judgements.status_code != 200:
        raise FailToCatchContestError
    contest_name = requests.get(f'{url}/contests/{contest_id}', auth=auth)
    contest_name = decode_json(contest_name)['formal_name']
    AC = decode_json(judgements)
    subs = [x['submission_id'] for x in AC if x['judgement_type_id'] == 'AC']
    res = []
    for sub_id in subs:
        student_id = requests.get(f'{url}/contests/{contest_id}/submissions/{sub_id}?strict=false', auth=auth)
        student_id = decode_json(student_id)
        if 'code' in student_id:
            continue
        student_id, time = str(student_id['team_id']), str(student_id['time'])[:19]
        if len(student_id) < 8:
            continue
        source_code = requests.get(f'{url}/contests/{contest_id}/submissions/{sub_id}/source-code', auth=auth)
        source_code = decode_json(source_code)
        source_code = str(base64.b64decode(source_code[0]['source']), encoding='UTF-8', errors='ignore')
        res.append({
            'id': student_id,
            'time': time,
            'code': source_code
        })
    while True:
        try:
            zip_name = contest_name + '.zip'
            with ZipFile(zip_name, 'x') as z:
                dup = {}
                for x in res:
                    if x['id'] in dup:
                        file_name = x['id'] + '-' + str(dup[x['id']]) + '_' + x['time']
                        dup[x['id']] += 1
                    else:
                        file_name = x['id'] + '_' + x['time']
                        dup[x['id']] = 1
                    with z.open(file_name + '.cpp', 'w') as f:
                        f.write(bytes(x['code'], encoding='UTF-8', errors='ignore'))
            print('下載完成')
            break
        except FileExistsError:
            print(f'請將{zip_name}刪除')
            os.system('pause')
            continue
