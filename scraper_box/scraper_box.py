import os

import modules.requirements
import modules.tools.plaform_dependant as pd
import modules.tools.tag as t
from modules.tools import choices

modules_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "modules")
req = modules.requirements.Requirements(modules_path)
local_scrapers_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "scrapers")

available_modules = req.get_available()

tag = t.tag


def main_menu():
    global available_modules
    show_logo()
    opts = ["Scraper Tests", "Tools", "Update", "Help"]
    option = choices.get_choice("Please Choose An Option From The Menu", "Enter Choice", opts, False)
    if option is False:
        exit()
    if option is 1:
        choose_scraper_source()
    if option is 2:
        tool_menu()
    if option is 3:
        if req.update_required() is True:
            available_modules = req.get_available()
            main_menu()
    if option is 4:
        help_menu()  # @TODO Add Help Text


def choose_scraper_source():
    show_logo()
    sources = []
    opts = ["Local", "All"]
    if len(available_modules) > 1:
        opts.append("Multiple")
    for module in available_modules:
        for key in module:
            opts.append(key.replace('_', '.'))
    option = choices.get_choice("Please Choose Your Scraper Source", "Enter Choice", opts, True)
    if option is False:
        main_menu()
    if "Multiple" in option:
        sources = []
        opts = ["Finished Picking"]
        for module in available_modules:
            for key in module:
                opts.append(key)
        while opts > 2:
            show_logo()
            option = choices.get_choice("Please Choose Your Scraper Source", "Enter Choice", opts, True)
            while option is not False and "Finished Picking" not in option:
                sources.append(option)
                opts[:] = [d for d in opts if d != option]
            if option is False:
                main_menu()
            if "Finished Picking" in option:
                if sources:
                    scraper_testing_menu(sources)
                else:
                    main_menu()
    for module in available_modules:
        for key in module:
            if option.replace('.', '_') in key:
                scraper_testing_menu([option])
    if "Exit" in option:
        main_menu()
    if "Local" in option:
        sources.append("Local")
        scraper_testing_menu(sources)
    if "All" in option:
        sources.append("All")
        scraper_testing_menu(sources)


def tool_menu():
    global available_modules
    show_logo()
    opts = []
    if len(available_modules) > 0:
        opts.append("Show Modules")
    opts = ["Add Module"]
    if available_modules:
        opts.append("Edit Module")
        opts.append("Delete Module")
    if req.show_tag():
        opts.append("Disable Shitty Logo")
    else:
        opts.append("Enable Shitty Logo")
    option = choices.get_choice("Select Option From Below.", "Enter Option", opts, True)
    if option is False:
        main_menu()
    if "Show Modules" in option:
        pass
    if "Add Modules" in option:
        if req.add_module() is True:
            available_modules = req.get_available()
            show_logo()
            opts = ["Update Now"]
            option = choices.get_choice("Module Not Available Until Update Ran, Update Now?", "Enter Choice", opts,
                                        False)
            if option == 1:
                if req.update_required() is True:
                    available_modules = req.get_available()
    if "Edit Module" in option:
        req.edit_module()
        available_modules = req.get_available()
    if "Delete Module" in option:
        req.delete_module(modules_path)
        available_modules = req.get_available()
    if "Logo" in option:
        req.toggle_tag()
    main_menu()


def help_menu():
    pass


def scraper_testing_menu(sources):
    scrapers = get_scrapers(sources)
    show_logo()
    opts = ["Test Scraper"]
    if len(sources) > 1:
        opts.append("Test Scrapers (Multiple)")
        opts.append("Test All Scrapers")
    option = choices.get_choice("Please Choose A Scraper Volume", "Enter Choice", opts, False)
    if option is False:
        main_menu()
    if option is 1:
        show_logo()
        if len(sources) > 1:
            opts = []
            for scraper in scrapers:
                for key in scraper:
                    opts.append(key)
            option = choices.get_choice("PLease choose scraper to test.", "Enter Choice", opts, True)
        else:
            option = source
    if option is 2:
        pass
    if option is 3:
        pass


def test_scrapers(names_list):
    show_logo()
    for name in names_list:
        name_parts = name.split('-')
        module = name_parts[0]
        scraper = name_parts[1]
        scraper_path = get_module_scraper_path(module)
        full_scraper_path = os.path.join(scraper_path, scraper)


def get_scrapers(source_=None):
    if source_ is None:
        source_ = ["Local"]
    scrapers = []

    for source in source_:
        if "Local" in source:
            for scraper_ in os.listdir(local_scrapers_dir):
                if "init" in scraper_:
                    continue
                scrapers.append({scraper_: local_scrapers_dir})
        if "All" in source:
            for scraper_ in os.listdir(local_scrapers_dir):
                print scraper_
                if "init" in scraper_:
                    continue
                scrapers.append({scraper_: local_scrapers_dir})
                print scrapers
            for module in available_modules:
                module_scrapers_dir = module['scraper_path']
                for scraper_ in os.listdir(module_scrapers_dir):
                    if "init" in scraper_:
                        continue
                    scrapers.append({scraper_: module_scrapers_dir})

        if "Local" not in source and "All" not in source:
            scrapers_dir = os.path.join(modules_path, source.replace('.', '_'), get_module_scraper_path(source))
            for scraper_ in os.listdir(scrapers_dir):
                if "init" in scraper_:
                    continue
                scrapers.append({scraper_: local_scrapers_dir})

    return scrapers


def is_module_available(name):
    for module in available_modules:
        if name in module:
            return True
    return False


def get_module_path(name):
    if is_module_available(name):
        for module in available_modules:
            if name in module:
                return module[name]['path']
    return False


def get_module_scraper_path(name):
    if is_module_available(name.replace('.', '_')):
        for module in req.requirements['modules']:
            if name in module['name']:
                return module['scraper_location']
    return False

def show_logo():
    pd.clear_screen()
    if req.show_tag():
        print tag


if __name__ == "__main__":
    main_menu()
