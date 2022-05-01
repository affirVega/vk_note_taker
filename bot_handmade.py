from dataclasses import dataclass
import requests

MESSAGE_NEW = 'message_new'
MESSAGE_REPLY = 'message_reply'
MESSAGE_EDIT = 'message_edit'
MESSAGE_ALLOW = 'message_allow'
MESSAGE_DENY = 'message_deny'
MESSAGE_EVENT = 'message_event'

@dataclass
class Update:
    type: str
    object: dict
    group_id: int

class Longpoll:
    def __init__(self, session, api, group_id, wait = 25):
        self.session = session
        self.api = api
        self.group_id = group_id
        self.wait = wait
        
        self.update_longpoll()


    def get(self) -> list[Update]:
        response = requests.get(self.server, {
            'ts':self.ts,
            'key':self.key,
            'wait':self.wait,
            'act':'a_check',
        }).json()
        if 'failed' in response:
            error_code = response['failed']
            if error_code == 1:
                self.ts = response['ts']
            elif error_code == 2 or error_code == 3:
                self.update_longpoll()
            return []

        self.ts = response['ts']
        updates = []
        for update in response['updates']:
            updates.append(Update(
                type=update['type'],
                object=update['object'],
                group_id=update['group_id'],
            ))
        return updates


    def update_longpoll(self):
        response = self.api.groups.getLongPollServer(group_id=self.group_id)
        self.key = response['key']
        self.server = response['server']
        self.ts = response['ts']

