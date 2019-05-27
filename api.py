import requests
from time import sleep
from datetime import datetime



class api_vk:
    def __init__(self, login, password):

        client_id = 3140623
        #client_secret = hHbZxrka2uZ6jB1inYsH'
        client_secret = "VeWdmVclDCtn6ihuP1nt"


        scope = "notify,photos,friends,audio,video,notes,pages,docs,status,questions,offers,wall,groups,messages," \
                "notifications,stats,ads,offline"
        url = f"http://oauth.vk.com/token?client_id={client_id}&client_secret={client_secret}&grant_type=password&" \
              f"username={login}&password={password}&scope={scope}"

        self.s = requests.Session()
        data = self.s.get(url).json()

        self.token = data['access_token']

        self.id = data['user_id']
        self.api = 'https://api.vk.com/method/'

    def getCounters(self):
        return self.s.get(
            self.api + 'account.getCounters',
            params={'access_token': self.token}).json()['response']

    def userGet(self, i):
        #i = list(i)
        #print(i)



        data = self.s.post(
            self.api + 'users.get',
            params={
                'user_ids': i,
                'access_token': self.token
            }).json()
        #print(data)
        data = data['response']
        #print(len(data), len(*i))

        return [k['first_name'] + ' ' + k['last_name'] for k in data]

    def setOffline(self):
        self.s.post(
            self.api + 'account.setOffline',
            params={'access_token': self.token})

    def setOnline(self):
        self.s.post(
            self.api + 'account.setOnline',
            params={'access_token': self.token})

    def send(self, friend, message):
        self.s.post(
            self.api + 'messages.send',
            params={
                'access_token': self.token,
                'user_id': friend,
                'message': message
            })

    def server(self):

        return self.s.get(
            self.api + 'messages.getLongPollServer',
            params={
                'access_token': self.token,
                'need_pts': '1',
                'ip_version': '3'
            }).json()['response']

    def longPoll(self):

        return self.s.get(
            'https://{server}?act=a_check&key={key}&ts={ts}&wait=25&mode=2&version=2'.
            format(
                server=self.server()['server'],
                key=self.server()['key'],
                ts=self.server()['ts'])).json()

    def getHistory(self):
        ts = self.server()['ts']
        pts = self.server()['pts']
        return self.s.get(
            self.api + 'messages.getLongPollHistory',
            params={
                'access_token': self.token,

                'ts': ts,
                'pts': pts,
                'ip_version': '3'
            }).json()

    def friends(self, a = 1):
        data = self.s.post(
            self.api + 'friends.get',
            params={
                'access_token': self.token,
                'order': 'hints',
                'user_id': self.id,
            }).json()['response']
        #print(data)

        ids = ','.join(map(str, data))

        #print(f'ids:{ids}')
        names = self.userGet(ids)



        #print(len(names), len(data))
        res = {}
        for i in range(len(data)):
            if a:
                res[names[i]] = data[i]
            else:
                res[data[i]] = names[i]

        return res

    def getDialog(self, i):

        return self.s.get(
            self.api + 'messages.getHistory',
            params={'access_token': self.token,
                    'user_id': i}).json()['response'][0:]

    def myMessages(self, friend):
        a = []
        data = self.getDialog(friend)
        for i in range(len(data)):
            if data[i]['from_id'] == self.id:
                a.append(data[i])
        return a

    def newsfeed(self, count=1):
        data = self.s.get(
            self.api + 'newsfeed.get',
            params={'access_token': self.token,
                    'count': count}).json()
        return data

    def getAttachments(self, friend, media='audio'):
        a = []
        data = self.s.get(
            self.api + 'messages.getHistoryAttachments',
            params={
                'access_token': self.token,
                'media_type': media,
                'peer_id': self.friends()[friend]
            }).json()['response']

        if media == 'audio':

            for i in range(1, len(data) - 1):
                b = data[str(i)][media]
                artist = b['artist']
                title = b['title']
                url = b['url']
                name = title + ' ' + artist + '.mp3'

                with open(name, 'wb') as target:
                    target.write(requests.get(url).content)
                    target.close()

                a.append([artist, title, url])

        elif media == 'photo':
            for i in range(1, len(data) - 1):
                print(i)

                b = data[str(i)][media]
                k = 0

                url = b['src_' + k * 'x' + 'big']

                with open(str(i) + '.png', 'wb') as target:
                    target.write(requests.get(url).content)

        return a

    def newMessages(self):
        friends = [*self.friends().values()][:5]
        friends = [*map(str, friends)]
        #print(friends)

        message = [self.getDialog(friend) for friend in friends]
        
        a = {}

        for i in message:

            if i != []:

                k = 1
                s = []
                while i[k]['read_state'] == 0:
                    s.append(i[k])
                    k += 1
                if len(s) > 0:

                    a[self.userGet(friends[k-1])[0]] = s
        return a


    def pm24(self):
        data = self.s.get(
            self.api + 'messages.getHistory',
            params={'access_token': self.token,
                    'chat_id': 123}).json()['response'][1:]
        #print(data)
        n = [i['from_id'] for i in data]
        ids = ','.join(map(str, n))
        names = self.userGet(ids)

        data_new = [{
            names[i]: {
                'body':
                data[i]['body'],
                'time':
                datetime.fromtimestamp(data[i]['date'])
                .strftime('%Y-%m-%d %H:%M:%S')
            }
        } for i in range(len(data))]
        for i in reversed(data_new):
            print('{}: {}\n{}\n'.format(*i.keys(
            ), dict(*i.values())['body'], dict(*i.values())['time']))
        # print(i)


def toFile():
    with open('data.py', 'w') as file:
        file.write('data = ' + str(a.getCounters()))


if __name__ == '__main__':
    login = input('Enter your login: ')
    password = input('Enter your password: ')
    vk = api_vk(login, password)
    print(vk.newMessages())
