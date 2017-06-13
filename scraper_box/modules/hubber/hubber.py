# -*- coding: utf-8 -*-
import json
import os
import urllib2
from urlparse import urljoin

import requests

debug = False
github_api_url = 'https://api.github.com'


class Hubber(object):
    def __init__(self, modules_path, oauth2_token):
        self.modules_path = modules_path
        self.download_queue = []
        self.oauth2_token = oauth2_token
        self.target = None

    def get_json_tree_info(self, repo_owner, repo_name, target):
        url = "/repos/" + repo_owner + '/' + repo_name + '/contents/' + target

        etag_for_conditional = self.get_etag(target)

        try:
            request_headers = {
                "Accept-Language": "en-US,en;q=0.5",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
                "Accept": "application/vnd.github.v3+json",
                "Connection": "keep-alive",
                "Authorization": "token " + self.oauth2_token,
                "If-None-Match": etag_for_conditional
            }
            request = urllib2.Request(github_api_url + url, headers=request_headers)
            try:
                attempt = urllib2.urlopen(request)
                request_information = attempt.info()
                if debug is True:
                    for item in request_information:
                        print item + ': ' + request_information[item]
                etag = attempt.info()['etag']
                self.store_etag(target, etag)
                try:
                    json_to_convert = attempt.read()
                except:
                    raise IOError
                try:
                    converted_json = json.loads(json_to_convert)
                except:
                    raise ValueError
                return converted_json
            except urllib2.HTTPError, e:
                if e.getcode() == 304:
                    return None
        except Exception:
            import traceback
            print 'generic exception: ' + traceback.format_exc()
            exit(1)

    @staticmethod
    def process_json_tree_info(json_tree_info):
        files = []
        directories = []

        for item in json_tree_info:
            if 'file' in item['type']:
                _file = {
                    "name": item['name'],
                    "download_url": item['download_url'],
                    "path": item['path'],
                }
                files.append(_file)

            if 'dir' in item['type']:
                _dir = {
                    "name": item['name'],
                    "path": item['path']
                }
                directories.append(_dir)

        return files, directories

    def get_target(self, repo_owner, repo_name, target):
        self.target = target
        structure = self.get_json_tree_info(repo_owner, repo_name, target)
        if structure is not None:
            files, directories = self.process_json_tree_info(structure)
            for _file in files:
                self.download_queue.append(_file)
            for _dir in directories:
                self.get_target(repo_owner=repo_owner, repo_name=repo_name, target=_dir['path'])
        if self.download_queue:
            return True
        else:
            return False

    @staticmethod
    def load_etags():
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), "etags.json")):
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "etags.json"), 'r') as f:
                etags = json.load(f)
            return etags
        return None

    @staticmethod
    def store_etags(etags):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "etags.json"), 'wb') as f:
            json.dump(etags, f)

    def get_etag(self, target):
        etags = self.load_etags()
        if etags is not None:
            if target in etags:
                return etags[target]
        return None

    def store_etag(self, target, new_etag):
        etags = self.load_etags()
        if etags is not None:
            etags[target] = new_etag
            self.store_etags(etags)
        else:
            etags = {target: new_etag}
            self.store_etags(etags)

    def delete_etags(self, target):
        etags = self.load_etags()
        to_delete = []
        for etag in etags:
            if target in etag:
                to_delete.append(etag)
        for del_tag in to_delete:
            del etags[del_tag]
        self.store_etags(etags)

    def process_download_queue(self):
        for download_object in self.download_queue:
            path_parts = download_object['path'].split('/')
            store_path = self.modules_path
            for part in path_parts:
                if not download_object['name'] in part:
                    part = part.replace('.', '_')
                store_path = os.path.join(store_path, part)
            dir_path = store_path.replace(os.sep + download_object['name'], '').replace('.', '_')
            if not os.path.isdir(store_path.replace(os.sep + download_object['name'], '')):
                os.mkdir(dir_path)

            url = download_object['download_url']
            file_name = url.split('/')[-1]
            u = urllib2.urlopen(url)
            f = open(store_path, 'wb')
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print "Downloading: %s Bytes: %s" % (file_name, file_size)

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                status = r"%10d  [%3.2f%%] " % (file_size_dl, file_size_dl * 100. / file_size)
                status += chr(8) * (len(status) + 1)
                print status,

            f.close()
            self.download_queue[:] = [d for d in self.download_queue if d.get('name') != self.target]

            if not os.path.isfile(os.path.join(dir_path, '__init__.py')):
                open(os.path.join(dir_path, '__init__.py'), 'a').close()

        if self.download_queue:
            return False
        return True


class HubberToken:
    def __init__(self):
        pass

    @staticmethod
    def get_token_from_github():
        print "Please enter details so we can obtain an outh2 token from github."
        print "Only token is stored (modules/required.json)"
        username = raw_input('Github username: ')
        password = raw_input('Github password: ')
        url = urljoin(github_api_url, 'authorizations')
        payload = {"note": 'scraper_box_token'}
        result = requests.post(url, auth=(username, password), data=json.dumps(payload))
        encoded_json = json.loads(result.text)
        if result.status_code >= 400:
            message = encoded_json.get('message', 'UNDEFINED ERROR (no error description from server)')
            print 'ERROR: %s' % message
            print 'Status Code: %s' % str(result.status_code)
            exit(1)
        return encoded_json['token']
