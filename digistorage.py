import json
import requests
import yaml

API_BASE = 'https://storage.rcs-rds.ro'
DEFAULT_MOUNT_NAME = 'Digi Cloud'


class DigiStorageApi:
    def __init__(self, mount_name=DEFAULT_MOUNT_NAME):
        self.config = yaml.load(open('config.yaml'))
        self.session = requests.Session()
        self.token = self.__init_token()
        self.session.headers['Authorization'] = 'Token ' + self.token
        self.mounts = self.__init_mounts()
        self.mount = self.get_mount_by_name(mount_name)

    def __init_token(self):
        headers = {
            'Accept': '*/*',
            'X-Koofr-Password': self.config['password'],
            'X-Koofr-Email': self.config['email']
        }
        r = requests.get(API_BASE + '/token', headers=headers)
        if r.status_code != 200:
            raise Exception('Error authenticating. Wrong username/password?')

        return r.headers['X-Koofr-Token']

    def __init_mounts(self):
        return self.session.get(API_BASE + '/api/v2/mounts').json()['mounts']

    def get_mount_by_name(self, mount_name):
        found_mounts_with_name = [m for m in self.mounts if m['name'] == mount_name]
        if not found_mounts_with_name:
            raise Exception('No mount has been found under the name: ' + mount_name)
        return found_mounts_with_name[0]

    def upload(self):
        pass

    def upload_file(self, file_path, remote_path, remote_file_name):
        """ remote_path = path without the file name, with no / at the beginning """
        with open(file_path) as f:
            r = self.session.post(API_BASE + '/content/api/v2/mounts/' + self.mount['id'] + '/files/put',
                                  params={'path': '/' + remote_path},
                                  files={'file': (remote_file_name, f.read())}
                                  )
            f.close()
            if r.status_code != 200:
                raise Exception('Error uploading file')
            return r

    def create_folder(self, remote_path):
        """ remote_path = full path containing the folder name, with no / at the beginning """
        r = self.session.post(API_BASE + '/api/v2/mounts/' + self.mount['id'] + '/files/folder',
                              params={'path': '/'},
                              data=json.dumps({'name': remote_path}),
                              headers={'content-type': 'application/json'}
                              )
        if r.status_code != 200:
            raise Exception('Error creating folder')
        return r


if __name__ == '__main__':
    dsa = DigiStorageApi()
    dsa.create_folder('caca')
    dsa.upload_file('README.md', remote_path='caca', remote_file_name='README.md')
    pass
