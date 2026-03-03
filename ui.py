'''Module who makes the user interface'''
# ui.py

# Replace the following placeholders with your information.

# MIA DESIREE ABURTO
# MABURTO@UCI.EDU
# 12216719

import sys
import os
from pathlib import Path
import Profile as p
import ds_client as client
from OpenWeather import OpenWeather
from LastFM import LastFM


class PortHolder:
    '''class to edit port'''

    def __init__(self, port):
        self.port = port

    def edit_port(self):
        '''edit port number'''
        new_port = input('>>> Enter new port: ')
        self.port = new_port
        return self.port

    def print_port(self):
        '''print port number'''
        print('Port number:', self.port)

    def get_port(self):
        '''gets port number'''
        return int(self.port)


port_holder = PortHolder(port=3021)


def file_error(path_str: str) -> None:
    '''Function to check if the O command works:
    it checks if it is a file isntead of a directory '''
    if '.dsu' in path_str:
        print('>>> Not able to create file in .dsu file')
        main(commands=['O', 'C', 'D'])
    elif '.py' in path_str:
        print('>>> Not able to create file in .py file')
        main(commands=['O', 'C', 'D'])
    elif '.txt' in path_str:
        print('>>> Not able to create file in .tzt file')
        main(commands=['O', 'C', 'D'])


def run(command, my_path):
    '''Runs: looks for the command to run'''
    if command == 'C':
        file_error(my_path)
        my_path = Path(my_path)
        command_c(my_path)
    elif command == 'O':
        my_path = Path(my_path)
        command_o(my_path)
    else:
        print('>>> Main command not found'.strip('/n'))


def command_c(my_path):
    '''Function to create a file'''
    my_path = Path(my_path)

    created_file = input('>>> Enter file name to be created: ')
    new_path = os.path.join(str(my_path), f'{created_file}.dsu')
    checks = Path(new_path)
    if checks.exists():
        print('>>> File already exists...Loading...')
        command_o(checks)
    else:
        username = input('>>> Enter username: ')
        check_space(username)

        password = input('>>> Enter password: ')
        check_space(password)

        print('>>> Since you are a new user...(you only need to do this once)')
        dsu_server = input('>>> Enter dsu_server:')

        with open(new_path, 'w', encoding='utf') as created_file:
            profile = p.Profile(dsuserver=dsu_server,
                                username=username, password=password)
            file_name = created_file.name
            profile.save_profile(str(file_name))
            created_file.close()
            menu(file_name)


def menu(created_file):
    '''Function to print menu options'''
    print()
    print('--------------MENU---------------')
    print()
    print('Edit Profile [E]')
    print('Print Profile [P]')
    print('Quit [Q]')
    next_command = input('Choose an option please: ')

    if next_command == 'E':
        command_e(created_file)
    elif next_command == 'P':
        command_p(created_file)
    elif next_command == 'Q':
        print('...Quitting...')
        sys.exit()
    else:
        print('>>> Command not found. Try Again.')
        menu(created_file)

    return next_command


def command_o(my_path):
    '''function to load a file'''
    string = str(my_path)

    if not string.endswith('.dsu'):
        print('>>> ERROR: Not a DSU file'.strip('/n'))
    else:
        with open(my_path, 'r', encoding="utf-8") as f:
            profile = p.Profile()
            profile.load_profile(str(my_path))
            print('>>> File has succesfully opened'.strip('/n'))
            print(f'>>> Hello {profile.username}!!'.strip('/n'))

        menu(my_path)
        f.close()


def check_space(var):
    '''function to check if var is empty or has whitespace'''
    if var.strip() == '' or ' ' in var:
        print('>>> Empty or whitespace is not allowed')
        return False
    return True


def ep_menu():
    '''function to print menu to ask for input
    on Edit and print command'''
    print()
    print(">>>        Other available commands        <<< ")
    print("Leave to Menu [type any character]")
    print("Print [P]")
    print("Edit [E]")
    print("Exit [Q]")
    action = input('Enter option: ')
    return action


def ep_menu_input(created_file):
    '''function which makes the action of EP menu'''
    print()
    print(">>>        Other available commands.        <<< ")
    print("Leave to Menu [type any character]")
    print("Print [P]")
    print("Edit [E]")
    print("Exit [Q]")
    action = input('Enter option: ')

    if action == 'Q':
        print('...Quitting...')
        sys.exit()
    elif action == 'E':
        command_e(created_file)
    elif action == 'P':
        command_p(created_file)
    else:
        main(commands=['O', 'C', 'D'])
    return action


def p_menu():
    '''Function to print out P menu'''
    print('>>>        PRINT OPTIONS        <<<')
    print()
    print('-usr [PRINTS USERNAME]')
    print('-pwd [PRINTS PASSWORD]')
    print('-bio [PRINTS BIO] ')
    print('-posts [PRINTS ALL POST]')
    print('-post [ID] [PRINTS POST BY ID]')
    print('-server [PRINTS SERVER ADDRESS]')
    print('-port [PRINTS PORT NUMBER]')
    print('-all [PRINTS EVERYTHING]')
    print()


def ask(username, password, post, server, bio=None):
    '''function to ask if they want to post to the server'''
    # port = 3021
    port = port_holder.get_port()
    action = input(
        '>>> Do you want to post this to the server? "Yes" or "No": ')
    if action == 'Yes':
        print('>>> You selected YES')

        if bio:
            b = client.send(server, port, username, password, post, bio)
        if post:
            new_post = transcluded_m(post)
            if new_post == 1:
                print('>>> Information not found: Not able to post')
                b = False
            elif new_post:
                b = client.send(server, port, username,
                                password, new_post, bio)
            else:
                print('>>> No keyword found, posting the message as it is')
                b = client.send(server, port, username, password, post, bio)
        if b is False:
            print('>>> Invalid parameter: Not able to send to server')
            print('>>> Returning home')
            main(commands=['O', 'C', 'D'])
    elif action == 'No':
        print('>>> You selected "NO"...continue')
    else:
        print('>>> Action not valid')
        ask(username, password, post, server, bio)


def command_p(created_file):
    '''prints out the contents within the profile module'''
    profile = p.Profile()
    profile.load_profile(str(created_file))
    action = 'P'

    while action == 'P':
        p_menu()
        options = input('Choose an option to print: ').split()

        for option in options:
            if option == '-usr':
                print('Username:', profile.username)
            elif option == '-pwd':
                print('Password:', profile.password)
            elif option == '-bio':
                print('Bio:', profile.bio)
                ask(profile.username, profile.password,
                    '', profile.dsuserver, profile.bio)
            elif option == '-posts':
                print("Posts in the profile:")
                for i, post in enumerate(profile.get_posts()):
                    i += 1
                    print(f"{i}.Time:{post.timestamp} Entry: {post.entry}")
                stri = '^^^ If your wish to print one '
                ng = 'of these posts select "-post" option! ^^^'
                print()
                print(stri+ng)
            elif option == '-post':
                index = int(
                    input('Enter number of post to print (starting from 1): '))
                for i, post in enumerate(profile.get_posts()):
                    i += 1
                    if index == i:
                        print(f"{i}.Time:{post.timestamp} Entry: {post.entry}")

                        ask(profile.username, profile.password,
                            post.entry, profile.dsuserver)

            elif option == '-server':
                print('Server address:', profile.dsuserver)

            elif option == '-port':
                port_holder.print_port()

            elif option == '-all':
                print()
                print('Server address:', profile.dsuserver)
                print('Username:', profile.username)
                print('Password:', profile.password)
                print('Bio:', profile.bio)
                print("Posts in the profile:")
                for i, post in enumerate(profile.get_posts()):
                    i += 1
                    print(f"{i}.Time:{post.timestamp} Entry: {post.entry}")

        profile.save_profile(str(created_file))
        action = ep_menu_input(str(created_file))

    if action == 'Q':
        print('...Quitting...')
        sys.exit()
    elif action == 'E':
        command_e(created_file)
    else:
        main(commands=['O', 'C', 'D'])


def e_menu():
    '''prints out the E menu available options'''
    print()
    print('>>>        OPTIONS TO EDIT        <<<')
    print('-usr [YOUR USERNAME]')
    print('-pwd [YOUR PASSWORD]')
    print('-bio [YOUR BIO] ')
    print('-addpost [YOUR NEW POST]')
    print('-delpost [YOUR ID]')
    print('-dsuserver [SERVER ADDRESS]')
    print('-editport [PORT NUMBER]')
    print()
    print('Write with the dash: e.g. "-usr"')
    return True


def e_checkempty(var, path):
    '''checks for empty, calls again if so'''
    if var.strip() == '':
        print()
        print('>>> EMPTY SUBMISSION IS NOT ALLOWED')
        print()
        command_e(path)
        return True
    return True


def transcluded_m(message):
    '''calls the api to transclude'''
    print('You can also leave it blank we have default values!')
    if '@weather' in message:
        apikey = '51c14ef187e0c51311a07d728ea27b5b'
        zips = input('>>> Enter zip code:')
        ccode = input('>>> Enter country code: ')
        apikey = input('>>> Enter API KEY: ')
        if not apikey or len(apikey.strip()) == 0:
            apikey = '51c14ef187e0c51311a07d728ea27b5b'
        if not zips or len(zips.strip()) == 0:
            zips = '92697'
        if not ccode or len(ccode.strip()) == 0:
            ccode = 'us'
        weather_object = OpenWeather(zips, ccode)
        weather_object.set_apikey(apikey)
        check = weather_object.load_data()
        if check:
            message = weather_object.transclude(str(message))
            return message
        return 1
    if '@lastfm' in message:
        apikey = '2123271d41900e1de08ff50a71db2d3f'
        artist = input('>>> Enter artist name: ')
        apikey = input('>>> Enter API KEY: ')
        if not apikey or len(apikey.strip()) == 0:
            apikey = '2123271d41900e1de08ff50a71db2d3f'
        if not artist or len(artist.strip()) == 0:
            artist = 'Lady Gaga'
        music_obj = LastFM(artist)
        music_obj.set_apikey(apikey)
        check = music_obj.load_data()
        if check:
            message = music_obj.transclude(str(message))
            return message
        return 1
    return False


def command_e(created_file):
    '''function to edit the contents
    of the profile file'''
    def edit_port():
        '''edit port number'''
        port_holder.edit_port()

    def dsuserver():
        '''edit dsu server'''
        print(created_file)
        new_server = input('>>> Enter server address:')

        if check_space(new_server) is False:
            ep_menu_input(str(created_file))
        profile.dsuserver = new_server
        profile.save_profile(str(created_file))
        print(">>> Your edited server is: ", profile.dsuserver)

    def username(created_file):
        '''edit username'''
        print(created_file)
        new_username = input('>>> Enter username: ')
        if check_space(new_username) is False:
            ep_menu_input(str(created_file))
        else:
            profile.username = new_username
            profile.save_profile(str(created_file))
            print(">>> Your edited username is: ", profile.username)

    def password(created_file):
        '''edit password'''
        new_password = input('>>> Enter password: ')
        if check_space(new_password) is False:
            ep_menu_input(str(created_file))
        profile.password = new_password
        profile.save_profile(str(created_file))
        print(">>> Your edited password is:", profile.password)

    def bio(created_file):
        '''edit bio'''
        bio = input('>>> Enter bio: ')
        e_checkempty(bio, created_file)
        profile.bio = bio
        profile.save_profile(str(created_file))
        print(">>> Your edited bio is:", profile.bio)
        ask(profile.username, profile.password,
            '', profile.dsuserver, profile.bio)

    def add_post():
        '''add post'''
        print()
        print('>>> Before you write your post here are the keywords:')
        s = '>>> "@weather": Replaces with the '
        print(s + 'current weather of your choice')
        print('>>> "@lastfm": Replaces with the top track of artist of choice')
        text = input('>>> Write your post!: ')
        e_checkempty(text, created_file)
        post = p.Post(entry=text)
        profile.add_post(post)
        print('>>> (epoch) Timestamp:', post.timestamp)
        print('>>> You added the following post:', post.entry)

        ask(profile.username, profile.password, post.entry, profile.dsuserver)

    def del_post():
        '''deletes a post by index'''
        gettingposts = profile.get_posts()
        print('Your notes:')

        for i, post in enumerate(gettingposts):
            print(i+1, post.entry)

        try:
            delete_i = int(
                input('>>> Choose the number of the post to delete: '))
            if delete_i > len(gettingposts):
                print('>>> Post number does not exist')
            else:
                profile.del_post(delete_i-1)
                print('>>> Post', delete_i, 'is now deleted')

        except IndexError:
            print('>>> Post number does not exist, cannot erase post')
        except ValueError:
            print('>>> Value Error cannot erase post')

    profile = p.Profile()
    profile.load_profile(str(created_file))
    action = 'E'
    while action == 'E':
        e_menu()
        options = input('>>> Enter a(n) option(s) from the menu: ').split()
        for option in options:
            if option == '-usr':
                username(created_file)
            elif option == '-pwd':
                password(created_file)
            elif option == '-bio':
                bio(created_file)
            elif option == '-addpost':
                add_post()
            elif option == '-delpost':
                del_post()
            elif option == '-dsuserver':
                dsuserver()
            elif option == '-editport':
                edit_port()
            else:
                print('>>> Option not found...')
                break

        profile.save_profile(str(created_file))
        action = ep_menu_input(str(created_file))


def get_inputs(commands):
    '''gets the first inputs to start program'''
    welcome = '>>> Welcome! Do you want to create or load a DSU file'
    choose = "('C' to create, 'O' to open/load, 'Q' to quit): "
    command = input(welcome+choose)

    if command == 'Q':
        print('...Quitting...'.strip('/n'))
        sys.exit()
    elif command in commands:
        directory = input('>>> Enter directory path: ')
        if not os.path.exists(Path(directory)):
            print('>>> Path does not exist'.strip('/n'))
            main(commands)
    else:
        print('Command not found'.strip('/n'))
        main(commands)

    return command, directory


def main(commands: list) -> None:
    '''main function '''
    while True:
        try:
            command, user_path = get_inputs(commands)
        except TypeError:
            command, user_path = get_inputs(commands)
        run(command, user_path)
