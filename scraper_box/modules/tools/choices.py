def get_choice(message_string, prompt_string, options_list, return_option):
    try:
        print message_string
        print ''
        options_list.insert(0, "Exit")
        for index, value in enumerate(options_list):
            print str(index) + "." + str(value)
        print ''
    except:
        raise TypeError

    while True:
        try:
            choice = int(input(prompt_string + ": "))
        except:
            continue

        if choice in range(len(options_list)):
            break
    if choice == 0:
        return False
    if return_option is True:
        return options_list[choice]
    return choice
