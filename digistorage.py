import json
import os
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
        self.mount = self.__get_mount_by_name(mount_name)

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

    def __get_mount_by_name(self, mount_name):
        found_mounts_with_name = [m for m in self.mounts if m['name'] == mount_name]
        if not found_mounts_with_name:
            raise Exception('No mount has been found under the name: ' + mount_name)
        return found_mounts_with_name[0]

    def upload(self, path, remote_path):
        """
        Convenience method: uploads either a file or a folder
        :param path: path on disk to the file/folder to upload, with no trailing /
        :param remote_path: path to upload to, WITHOUT the file/folder name, with no / at the beginning
        :return: None (will raise exception on error)
        """
        if os.path.isdir(path):
            for file_name in os.listdir(path):
                self.upload_file(path + '/' + file_name, remote_path)
        else:
            self.upload_file(path, remote_path)

    def upload_file(self, file_path, remote_path, remote_file_name=None):
        """
        :param file_path: path on disk to the file to upload
        :param remote_path: path to upload to, WITHOUT the file name, with no / at the beginning
        :param remote_file_name: name of the file to upload to, defaults to the file name
        :return: response object (will raise exception on error)
        """
        if remote_file_name is None:
            file_path_head, remote_file_name = os.path.split(file_path)
        with open(file_path) as f:
            r = self.session.post(API_BASE + '/content/api/v2/mounts/' + self.mount['id'] + '/files/put',
                                  params={'path': '/' + remote_path},
                                  files={'file': (remote_file_name, f.read())}
                                  )
            f.close()
            if r.status_code != 200:
                raise Exception('Error uploading file: ' + file_path)
            return r

    def upload_files(self, file_paths, remote_path):
        """
        :param file_paths: array of paths on disk to files
        :param remote_path: path to upload to, WITHOUT the file name, with no / at the beginning
        :return: None (will raise exception on error)
        """
        for file_path in file_paths:
            self.upload_file(file_path, remote_path)

    def create_folder(self, remote_path):
        """
        :param remote_path: full path containing the folder name, with no / at the beginning
        :return: response object (will raise exception on error)
        """
        r = self.session.post(API_BASE + '/api/v2/mounts/' + self.mount['id'] + '/files/folder',
                              params={'path': '/'},
                              data=json.dumps({'name': remote_path}),
                              headers={'content-type': 'application/json'}
                              )
        if r.status_code != 200:
            raise Exception('Error creating folder: ' + remote_path)
        return r

    def remove_file_folder(self, remote_path):
        """
        :param remote_path: full path containing the folder/file name, with no / at the beginning
        :return: response object (will raise exception on error)
        """
        r = self.session.delete(API_BASE + '/api/v2/mounts/' + self.mount['id'] + '/files/remove',
                                params={'path': '/' + remote_path},
                                )
        if r.status_code != 200:
            raise Exception('Error removing file/folder: ' + remote_path)
        return r

    def file_folder_info(self, remote_path):
        """
        :param remote_path: full path containing the folder/file name, with no / at the beginning
        :return: dict with file info; None if path does not exist
        """
        r = self.session.get(API_BASE + '/api/v2/mounts/' + self.mount['id'] + '/files/info',
                             params={'path': '/' + remote_path},
                             headers={'content-type': 'application/json'}
                             )
        if r.status_code != 200:
            return None
        return json.loads(r.content)


if __name__ == '__main__':
    dsa = DigiStorageApi()
    # dsa.create_folder('caca')
    # dsa.upload_file('README.md', remote_path='caca')
    # info = dsa.file_folder_info('caca/README.mdd')
    # dsa.upload('README.md', remote_path='')
    dsa.remove_file_folder('README.md')
    pass
