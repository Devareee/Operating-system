class Menu:
    def __init__(self, fs):
        self.fs = fs

    def prompt(self):
        while True:
            print(f'[{self.fs.current_user} {self.fs.current_path }~] $ ', end='')
            command = input().split()
            if len(command) == 0:
                continue

            if command[0] == 'ls' and len(command) == 1:
                if self.fs.access('', 'r', 1) == 1:
                    self.fs.ls()
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'touch' and len(command) == 2 and self.fs.find_file_offset(self.fs.current_offset, command[1]) == -1:
                if self.fs.access('', 'w', 1) == 1:
                    self.fs.create_file(self.fs.current_offset, command[1][:28], 0b01110, self.fs.get_uid(self.fs.current_user))
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'mkdir' and len(command) == 2 and self.fs.find_file_offset(self.fs.current_offset, command[1]) == -1:
                path = self.fs.current_path
                if self.fs.access('', 'w', 1) == 1:
                    self.fs.create_file(self.fs.current_offset, command[1][:28], 0b11110, self.fs.get_uid(self.fs.current_user))
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'rm' and len(command) == 2 and (self.fs.get_file_uid(command[1]) == self.fs.get_uid(self.fs.current_user) or self.fs.current_user == 'root') and command[1] != 'users':
                if self.fs.access('', 'w', 1) == 1:
                    file_path = self.fs.find_file_offset(self.fs.current_offset, command[1])
                    if file_path != -1:
                        self.fs.rm_file(file_path, self.fs.current_offset)
                    else:
                        print('Файл не существует')
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'cat' and len(command) == 2 and self.fs.get_attributes(self.fs.find_file_offset(self.fs.current_offset, command[1]))[0] == '0':
                if self.fs.access(command[1], 'w', 0) == 1:
                    file_path = self.fs.find_file_offset(self.fs.current_offset, command[1])
                    if file_path != -1:
                        print('Введите содержимое файла:')
                        data = input()
                        self.fs.write_data(file_path, data)
                    else:
                        print('Файл не существует')
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'rd' and len(command) == 2:
                if self.fs.access(command[1], 'r', 0) == 1:
                    file_path = self.fs.find_file_offset(self.fs.current_offset, command[1])
                    if file_path != -1:
                        print(self.fs.read_data(file_path))
                    else:
                        print('Файл не существует')
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'clr' and len(command) == 2:
                if self.fs.access(command[1], 'w', 0) == 1:
                    file_path = self.fs.find_file_offset(self.fs.current_offset, command[1])
                    if file_path != -1:
                        self.fs.clear(file_path)
                    else:
                        print('Файл не существует')
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'rnm' and len(command) == 3:
                if self.fs.access('', 'w', 1) == 1:
                    file_path = self.fs.find_file_offset(self.fs.current_offset, command[1])
                    if file_path != -1:
                        self.fs.rename(file_path, command[2][:28])
                    else:
                        print('Файл не существует')
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'cp' and len(command) == 3:
                if self.fs.access('', 'r', 1) == 1:
                    save = self.fs.current_offset
                    self.fs.current_offset = self.fs.cd(command[2])
                    if self.fs.access('', 'w', 1) == 1:
                        self.fs.current_offset = save
                        path = self.fs.find_file_offset(self.fs.current_offset, command[1])
                        new_path = self.fs.cd(command[2])
                        if path != -1 and new_path != -1:
                            self.fs.copy(path, new_path)
                        else:
                            print('Файл не существует')
                    else:
                        print('Недостаточно прав доступа')
                        self.fs.current_offset = save
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'mv' and len(command) == 3:
                if self.fs.access('', 'r', 1) == 1:
                    save1 = self.fs.current_offset
                    save2 = self.fs.current_path
                    self.fs.current_offset = self.fs.cd(command[2])
                    if self.fs.access('', 'w', 1) == 1:
                        self.fs.current_offset = save1
                        path = self.fs.find_file_offset(self.fs.current_offset, command[1])
                        new_path = self.fs.cd(command[2])
                        if path != -1 and new_path != -1:
                            self.fs.copy(path, new_path)
                            self.fs.current_offset = save1
                            self.fs.current_path = save2
                            self.fs.rm_file(path, self.fs.current_offset)
                        else:
                            print('Файл не существует')
                    else:
                        print('Недостаточно прав доступа')
                        self.fs.current_offset = save1
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'cd' and len(command) == 2 and self.fs.get_attributes(self.fs.find_file_offset(self.fs.current_offset, command[1].split('/')[-2]))[0] == '1':
                save1 = self.fs.current_offset
                save2 = self.fs.current_path
                self.fs.current_offset = self.fs.cd(command[1])
                if self.fs.access('', 'r', 1) == 1:
                    if self.fs.current_offset == -1:
                        print('Директория не существует')
                        self.fs.current_offset = save1
                        self.fs.current_path = save2
                else:
                    self.fs.current_offset = save1
                    self.fs.current_path = save2
                    print('Недостаточно прав доступа')

            elif command[0] == 'pwd' and len(command) == 1:
                print(self.fs.current_path)

            elif command[0] == 'chmod' and len(command) == 3:
                if self.fs.current_user == 'root' or self.fs.get_file_uid(command[2]) == self.fs.get_uid(self.fs.current_user):
                    self.fs.chmod(command[1], command[2])
                else:
                    print('Недостаточно прав доступа')

            elif command[0] == 'su' and len(command) == 1:
                self.enter()

            elif command[0] == 'adu' and len(command) == 2 and self.fs.current_user == 'root':
                login = command[1]
                print('Введите пароль:')
                password = input()
                a = self.fs.add_user(login[:15], password[:32])
                if a != -1:
                    print('Пользователь', command[1], 'добавлен')
                else:
                    print('Такой пользователь уже существует')

            elif command[0] == 'rmu' and len(command) == 2 and command[1] != 'root' and self.fs.current_user == 'root':
                self.fs.remove_user(command[1])
                print('Пользователь', command[1], 'удален')

            elif command[0] == 'users':
                self.fs.read_users()

            elif command[0] == 'help' and len(command) == 1:
                print('ls - просмотр содержимого текущего каталога\ntouch - создание файла\nmkdir - создание каталога\nrm - удаление файла'
                      '\ncat - запись в конец файла\nrd - чтение файла\nclr - очистка содержимого файла\nrnm - переименование\ncp - копирование'
                      '\nmv - перемещение файла\ncd - переход по каталогам\npwd - текущий путь\nchmod - смена прав доступа\nsu - смена пользователя'
                      '\nadu - добавление пользователя\nrmu - удаление пользователя\nusers - вывод пользователей')

            else:
                print('Команда не найдена')


    def enter(self):
        while True:
            print ('Введите логин:')
            login = input()
            print('Введите пароль:')
            password = input()
            if self.fs.check_user(login, password) == 1:
                self.fs.current_user = login
                self.prompt()
            else:
                print('Данные неправильные')
