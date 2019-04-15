#!/usr/bin/env python3
import argparse
import json
import os
import requests
import yaml

API_BASE = 'https://storage.rcs-rds.ro'


class DigiStorageApi:
    def __init__(self, mount_name='Digi Cloud', path_to_config='config.yaml', email=None, password=None):
        """
        :param mount_name: the remote folder to connect to
        :param path_to_config: the yaml config file
        :param email: (alternatively, if you don't want to use a config file)
        :param password: (alternatively, if you don't want to use a config file)
        """
        if email is None or password is None:
            config = yaml.load(open(path_to_config))
            email = config['email']
            password = config['password']
        self.session = requests.Session()
        self.token = self.__init_token(email, password)
        self.session.headers['Authorization'] = 'Token ' + self.token
        self.mounts = self.__init_mounts()
        self.mount = self.__get_mount_by_name(mount_name)

    @staticmethod
    def __init_token(email, password):
        headers = {
            'Accept': '*/*',
            'X-Koofr-Password': password,
            'X-Koofr-Email': email
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
            remote_file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--upload', type=str, required=False,
                        help='Path to file/folder to upload')
    parser.add_argument('--info', required=False, action='store_true',
                        help='Pass this param to get the info for the file/folder located @ remote_path')
    parser.add_argument('--mkdir', required=False, action='store_true',
                        help='Pass this param to create a directory @ remote_path')
    parser.add_argument('--rm', required=False, action='store_true',
                        help='Pass this param to delete the file/folder located @ remote_path')
    parser.add_argument('--remote_path', type=str, required=True,
                        help='Remote path to execute the desired action on')

    args = parser.parse_args()
    dsa = DigiStorageApi()

    if args.upload:
        dsa.upload(args.upload, remote_path=args.remote_path)
    elif args.info:
        print(dsa.file_folder_info(args.remote_path))
    elif args.mkdir:
        dsa.create_folder(args.remote_path)
    elif args.rm:
        dsa.remove_file_folder(args.remote_path)
