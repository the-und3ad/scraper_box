import json
import os

import hubber.hubber as hubber
import modules.tools.plaform_dependant as pd
import modules.tools.tag as t
import tools.choices as choices

tag = t.tag


class Requirements(object):
    def __init__(self, module_dir):
        self.module_dir = module_dir
        self.requirements = self.get_requirements()

    def get_requirements(self):
        try:
            with open(os.path.join(self.module_dir, 'required.json')) as f:
                requirements = json.load(f)
                return requirements
        except:
            try:
                with open(os.path.join(self.module_dir, 'required.json'), 'a') as f:
                    requirements = {
                        "oauth2_token": '',
                        "logo": True,
                        "modules": []
                    }
                    json.dump(requirements, f, indent=4, sort_keys=True)

            except:
                print "Was Unable To Create Requirements"
                exit(1)

    def update_required(self):
        required = self.requirements
        for module in required['modules']:
            print "Checking or bringing " + module['name'] + ' up to date.'
            hub = hubber.Hubber(self.module_dir, self.load_token())
            update = hub.get_target(repo_owner=module['repo_owner'], repo_name=module['repo_name'],
                                    target=module['name'])
            if update is True:
                print module['name'] + " has been updated, downloading updates."
                updated = hub.process_download_queue()
                if updated is True:
                    print "All files for %s successfully downloaded." % module['name']
                else:
                    print "Downloads for %s did not complete!" % module['name']
            else:
                print "No update required for " + module['name']
        print "Requirements Are Up To Date!"
        return True

    def get_available(self):
        available = []
        required = self.requirements
        for module in required['modules']:
            name = module['name'].replace('.', '_')
            if os.path.isdir(os.path.join(self.module_dir, name)):
                if os.listdir(os.path.join(self.module_dir, name)):
                    scraper_location = module['scraper_location'].split('/')
                    scraper_path = self.module_dir
                    for part in scraper_location:
                        scraper_path = os.path.join(scraper_path, part)
                    available.append({name: [{"path": self.module_dir, "scraper_path": scraper_path}]})
        return available

    def load_token(self):
        oauth2_token = self.requirements['oauth2_token']
        if oauth2_token == '':
            self.show_logo()
            print "We have no oauth token for you!"
            opts = ['Create and Store Token']
            option = choices.get_choice("Please choose from the following options.", "Enter Choice", opts, False)
            if option is 0:
                exit(0)
            if option is 1:
                hub = hubber.HubberToken()
                oauth2_token = hub.get_token_from_github()
                self.requirements['oauth2_token'] = oauth2_token
                self.store_requirements()
        return oauth2_token

    def store_requirements(self):
        with open(os.path.join(self.module_dir, 'required.json'), 'wb') as f:
            json.dump(self.requirements, f, indent=4, sort_keys=True)
        return True

    def show_tag(self):
        return self.requirements['logo']

    def toggle_tag(self):
        if self.requirements['logo'] == 'True':
            self.requirements['logo'] = "False"
        else:
            self.requirements['logo'] = "True"
        self.store_requirements()

    def add_module(self):
        self.show_logo()
        repo_owner = raw_input('Github Repo Owner: ')
        repo_name = raw_input('Github Repo Name: ')
        module_name = raw_input('Module Name: ')
        print "Please enter scraper location relative to main folder i.e for nan scrapers:"
        print "             lib/nanscrapers/scraperplugins"
        scraper_location = raw_input('Scraper Location: ')

        new_module = {
            "repo_owner": repo_owner,
            "name": module_name,
            "repo_name": repo_name,
            "scraper_location": scraper_location
        }

        self.requirements['modules'].append(new_module)
        self.store_requirements()
        return True

    def edit_module(self):
        self.show_logo()
        modules = self.requirements['modules']
        opts = []
        for module in modules:
            opts.append(module['name'])
        option = choices.get_choice("Select module to edit.", "Enter Choice", opts, True)
        if option is False:
            return
        for module in modules:
            if option in module['name']:
                self.show_logo()
                opts = [
                    "Module Name: %s" % module['name'],
                    "Repo Owner: %s" % module['repo_owner'],
                    "Repo Name: %s" % module['repo_name'],
                    "Scraper Location: %s" % module['scraper_location']
                ]
                edit = choices.get_choice("Select Item To Edit", "Enter Choice", opts, False)
                if edit is 0:
                    self.edit_module()
                if edit is 1:
                    module['name'] = raw_input('Module Name (%s): ' % module['name'])
                if edit is 2:
                    module['repo_owner'] = raw_input('Github Repo Owner (%s): ' % module['repo_owner'])
                if edit is 3:
                    module['repo_name'] = raw_input('Github Repo Name (%s): ' % module['repo_name'])
                if edit is 4:
                    print "Please enter scraper location relative to main folder i.e for nan scrapers:"
                    print "             lib/nanscrapers/scraperplugins"
                    module['scraper_location'] = raw_input('Scraper Location (%s): ' % module['scraper_location'])
                self.store_requirements()
                self.edit_module()

    def delete_module(self, modules_path):
        self.show_logo()
        modules = self.requirements['modules']
        opts = []
        for module in modules:
            opts.append(module['name'])
        option = choices.get_choice("Select module to Delete.", "Enter Choice", opts, True)
        if option is False:
            return
        self.show_logo()
        confirm = choices.get_choice("Confirm deletion of module: %s" % option, "Enter Choice", ["Confirm"], False)
        if confirm is False:
            return
        if confirm == 1:
            hub = hubber.Hubber(modules_path, self.requirements['oauth2_token'])
            self.requirements['modules'][:] = [d for d in self.requirements['modules'] if d.get('name') != option]
            self.store_requirements()
            hub.delete_etags(option)
            import shutil
            shutil.rmtree(os.path.join(modules_path, option.replace('.', '_')))

    def show_logo(self):
        pd.clear_screen()
        if "True" in self.show_tag():
            print tag
