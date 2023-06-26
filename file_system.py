import os.path
import time
import hashlib

class Filesystem:

    def __init__(self):
        file_path = '1.bin'
        self.root_offset = 12288
        self.current_offset = 12288
        self.users_offset = 16384
        self.current_user = 'root'

        self.uid = 0
        self.users_count = 0
        self.current_path = '/'

        if os.path.exists(file_path):
            self.f = open(file_path, "rb+")
            self.read_superblock()
        else:

            self.f = open(file_path, "w")
            self.f = open(file_path, "rb+")
            self.format()
            self.create_file(self.root_offset, "/", 0b11111, 0)
            self.users_offset = self.create_file(self.root_offset, "users", 0b00000, 0)
            self.add_user('root', '123')
            self.add_user('anya', '1')


    def format(self):
        self.type = 'file_system'
        self.block_size = 4096
        self.fs_size = 256
        self.inode_size = 8192
        self.free_blocks = 256
        self.free_inode = 136
        self.inode_card_size = 17
        self.blocks_card_size = 32

        self.current_offset = 12288
        a = '\0' * (1024 ** 2)
        self.f.write(a.encode('utf-8'))

        self.f.seek(0)
        self.f.write(self.type.encode('utf-8'))

        self.write(self.block_size, 2, 11)
        self.write(self.fs_size, 2, 13)
        self.write(self.inode_size, 4, 15)
        self.write(self.free_blocks, 4, 19)
        self.write(self.free_inode, 4, 23)
        self.write(self.inode_card_size, 4, 27)
        self.write(self.blocks_card_size, 4, 31)
        self.write(0b00001111, 1, 35)


    def read_superblock(self):
        self.type = self.f.read(11).decode('utf-8')
        self.block_size = self.read(2, 11)
        self.fs_size = self.read(2, 13)
        self.inode_size = self.read(4, 15)
        self.free_blocks = self.read(4, 19)
        self.free_inode = self.read(4, 23)
        self.inode_card_size = self.read(4, 27)
        self.blocks_card_size = self.read(4, 31)


    def write(self, data, size, offset):
        self.f.seek(offset)
        self.f.write(int(data).to_bytes(size, 'big'))


    def read(self, size, offset):
        self.f.seek(offset)
        data = self.f.read(size)
        data = int.from_bytes(data, 'big')
        return data


    def add_user(self, login, password):
        login += '\0' * (15 - len(login))

        pas = hashlib.sha256()
        pas.update(password.encode('utf-8'))
        pas = pas.digest()

        inode = self.read(4, self.users_offset+28)
        i = 0
        offset = 84 + inode * 54 + 2
        size = self.read(4, offset)
        address = self.get_inode_address(inode, i)
        save = address
        self.f.seek(address)
        self.f.seek(address + 1)
        b = self.f.read(15).decode('utf-8')
        address += 48
        while self.read(1, address) != 0:
            self.f.seek(address+1)
            log = self.f.read(15).decode('utf-8')
            if log == login or log == b:
                 return -1
            address += 48
            self.f.seek(address)
        address = save
        while address != 0:
            block_offset = address
            i += 1
            address = self.get_inode_address(inode, i)
        self.f.seek(block_offset + size % 4096)
        if size % 4096 != 0:
            self.write(self.uid, 1, block_offset + size % 4096)
            self.f.seek(block_offset + size % 4096 + 1)
            self.f.write(login.encode('utf-8'))
            self.f.seek(block_offset + size % 4096 + 16)
            self.f.write(pas)
        elif i < 10 and size % 4096 == 0:
            new_block = self.find_free_block()
            self.f.seek(new_block * 4096)
            self.write(self.uid, 1, block_offset + size % 4096)
            self.f.seek(block_offset + size % 4096 + 1)
            self.f.write(login.encode('utf-8'))
            self.f.seek(block_offset + size % 4096 + 16)
            self.f.write(pas)
            i += 1
        size += 48
        self.write(size, 4, offset)
        offset += 4
        date = int(time.time())
        self.write(date, 4, offset)
        self.create_file(self.root_offset, login, 0b11100, self.get_uid(login))
        self.uid += 1
        self.users_count += 1
        return 1


    def check_user(self, login, password):
        inode = self.read(4, self.users_offset + 28)
        j = 0
        address = self.get_inode_address(inode, j)
        pas = hashlib.sha256()
        pas.update(password.encode('utf-8'))
        pas = pas.digest()
        login += '\0' * (15 - len(login))
        a = ''
        while address != 0:
            i = address + 1
            self.f.seek(i)
            while login != a and self.f.read(15).decode('utf-8') != '':
                self.f.seek(i)
                a = self.f.read(15).decode('utf-8')
                if a == login:
                    i += 15
                    self.f.seek(i)
                    if self.f.read(32) == pas:
                        return 1
                    else:
                        return -1
                else:
                    i += 48
                    self.f.seek(i)
            j += 1
            address = self.get_inode_address(inode, j)
        return -1


    def read_users(self):
        inode = self.read(4, self.users_offset + 28)
        address = self.get_inode_address(inode, 0)
        self.f.seek(address)
        self.f.seek(address + 1)
        print(self.f.read(15).decode('utf-8'))
        address+=48
        while self.read(1, address) != 0:
            self.f.seek(address+1)
            print(self.f.read(15).decode('utf-8'))
            address += 48
            self.f.seek(address)


    def remove_user(self, login):
        inode = self.read(4, self.users_offset + 28)
        j = 0
        address = self.get_inode_address(inode, j)
        login += '\0' * (15 - len(login))
        a = ''
        while address != 0:
            i = address + 1
            self.f.seek(i)
            self.f.seek(address)
            while login != a and self.f.read(15).decode('utf-8') != '':
                self.f.seek(i)
                a = self.f.read(15).decode('utf-8')
                if a == login:
                    self.users_count -= 1
                    self.f.seek(i)
                    self.f.write(('rremoved' + '\0'*7).encode('utf-8'))
                else:
                    i += 48
                    self.f.seek(i)
            j += 1
            address = self.get_inode_address(inode, j)


    def ls(self):
        dir_offset = self.current_offset
        dir_offset += 28
        inode = self.read(4, dir_offset)
        i = 0
        offset2 = 84 + inode * 54 + 2
        size = self.read(4, offset2)
        count = size//32
        address = self.get_inode_address(inode, i)
        self.f.seek(address)
        j = 0
        while j != count:
            if self.f.read(1).decode('utf-8') != '\0':
                self.f.seek(address)
                name = self.f.read(28).decode('utf-8')
                address += 28
                inode2 = self.read(4, address)
                offset = 84 + inode2 * 54
                attributes = self.read(1, offset)
                offset += 1
                user_id = self.read(1, offset)
                offset += 1
                size = self.read(4, offset)
                offset += 4
                date = self.read(4, offset)
                date = time.ctime(date)
                attributes_str = ''
                attributes_str += 'd' if attributes & (1 << 4) != 0 else '-'
                attributes_str += 'r' if attributes & (1 << 3) != 0 else '-'
                attributes_str += 'w' if attributes & (1 << 2) != 0 else '-'
                attributes_str += 'r' if attributes & (1 << 1) != 0 else '-'
                attributes_str += 'w' if attributes & (1 << 0) != 0 else '-'
                print(attributes_str + '\t' + str(size) + '\t' + name + '\t' + str(self.get_user(user_id)) + '\t' + str(date))
                address -= 28
            address += 32
            j += 1
            i += 1
            self.f.seek(address)


    def create_file(self, offset, name, attributes, uid):
        self.f.seek(offset)
        name += '\0' * (28 - len(name))
        if self.read(1, offset) != 0:
            offset += 28
            inode = self.read(4, offset)
            offset2 = 84 + inode * 54 + 2
            size = self.read(4, offset2)
            i = 0
            address = self.get_inode_address(inode, i)
            while address != 0:
                self.f.seek(address)
                name_offset = address
                while name_offset != address+4096:
                    if self.read(1, name_offset) == 0:
                        self.f.seek(name_offset)
                        self.f.write(name.encode('utf-8'))
                        self.write(self.create_inode(attributes, uid), 4, name_offset + 28)
                        size += 32
                        self.write(size, 4, offset2)
                        break
                    else:
                        name_offset += 32
                offset += 4
                i += 1
                address = self.get_inode_address(inode, i)
            return name_offset

        else:
            self.f.seek(offset)
            self.f.write(name.encode('utf-8'))
            inode = self.create_inode(attributes, uid)
            self.write(inode, 4, offset + 28)
            return offset


    def find_file_offset(self, dir_offset, filename):
        filename += '\0' * (28 - len(filename))
        dir_offset += 28
        inode = self.read(4, dir_offset)
        i = 0
        address = self.get_inode_address(inode, i)
        while address != 0:
            self.f.seek(address)
            name_offset = address
            while name_offset != address + 4096:
                self.f.seek(name_offset)
                if self.f.read(28).decode('utf-8') == filename:
                    return name_offset
                else:
                    name_offset += 32
            dir_offset += 4
            i += 1
            address = self.get_inode_address(inode, i)
        return -1


    def rename(self, file_offset, new_name):
        self.f.seek(file_offset)
        new_name += '\0' * (28 - len(new_name))
        self.f.write(new_name.encode('utf-8'))


    def write_data(self, file_offset, data):
        file_offset += 28
        inode = self.read(4, file_offset)
        i = 0
        offset = 84 + inode * 54 + 2
        size = self.read(4, offset)
        blocks_count = self.read(4, offset+8)
        address = self.get_inode_address(inode, i)
        block_offset = address
        while address != 0:
            block_offset = address
            i += 1
            address = self.get_inode_address(inode, i)
        self.f.seek(block_offset + size % 4096)
        data1 = data[:4096 - size % 4096]
        data = data[len(data1):]
        size += len(data1)
        self.f.write(data1.encode('utf-8'))
        while i < 10 and data != "":
            data1 = data[:4096]
            data = data[4096:]
            new_block = self.find_free_block()
            self.f.seek(new_block*4096)
            self.f.write(data1.encode('utf-8'))
            size += len(data1)
            i += 1
            blocks_count += 1
        self.write(size, 4, offset)
        offset += 4
        date = int(time.time())
        self.write(date, 4, offset)
        self.write(blocks_count, 4, offset + 4)


    def read_data(self, file_offset):
        data = ""
        file_offset += 28
        inode = self.read(4, file_offset)
        i = 0
        offset = 84 + inode * 54 + 2
        size = self.read(4, offset)
        address = self.get_inode_address(inode, i)
        while address != 0 and i < 9 and size:
            self.f.seek(address)
            data += self.f.read(4096).decode('utf-8')
            i += 1
            address = self.get_inode_address(inode, i)
        data = data[:size]
        return data


    def rm_file(self, file_offset, dir_offset):
        self.f.seek(dir_offset)
        size = self.read(4, 84 + self.read(4, dir_offset+28) * 54 + 2)
        self.f.seek(file_offset)
        self.write(0, 1, file_offset)
        file_offset += 28
        inode = self.read(4, file_offset)
        self.f.seek(file_offset)
        self.f.write(('\0'*4).encode('utf-8'))
        i = 0
        offset = 84 + inode * 54 + 2
        size = self.read(4, offset)
        address = self.get_inode_address(inode, i)
        while address != 0 and i < 9:
            number = address//4096
            block = 35+(number//8)
            bit = number % 8
            data = self.read(1, block)
            data &= ~(1 << bit)
            self.write(data, 1, block)
            i += 1
            address = self.get_inode_address(inode, i)
        inodee = 67+inode//8
        bit = inode % 8
        data = self.read(1, inodee)
        data &= ~(1 << bit)
        self.write(data, 1, inodee)


    def copy(self, file_offset, dir_offset):
        self.f.seek(file_offset)
        name = self.f.read(28).decode('utf-8')
        file_offset += 28
        inode = self.read(4, file_offset)
        offset = 84 + inode*54
        self.f.seek(offset)
        attributes = self.read(1, offset)
        self.f.seek(offset+1)
        if self.read(1, dir_offset) != 0:
            dir_offset += 28
            inode = self.read(4, dir_offset)
            size = self.read(4, 84 + inode*54 + 2)
            size += 32
            i = 0
            address = self.get_inode_address(inode, i)
            while address != 0:
                self.f.seek(address)
                name_offset = address
                while name_offset != address + 4096:
                    if self.read(1, name_offset) == 0:
                        self.f.seek(name_offset)
                        self.f.write(name.encode('utf-8'))
                        self.write(self.create_inode(attributes, self.get_uid(self.current_user)), 4, name_offset + 28)
                        break
                    else:
                        name_offset += 32
                dir_offset += 4
                i += 1
                address = self.get_inode_address(inode, i)
            file_offset -= 28
            new_data = self.read_data(file_offset)
            self.write_data(name_offset, new_data)
            self.write(size, 4, 84 + inode*54 + 2)
            return name_offset


    def clear(self, file_offset):
        file_offset += 28
        inode = self.read(4, file_offset)
        i = 0
        offset = 84 + inode * 54 + 2
        self.write(0, 4, offset)
        self.write(0, 4, offset + 8)

        address = self.get_inode_address(inode, i)
        while address != 0 and i < 9:
            number = address // 4096
            block = 35 + (number // 8)
            bit = number % 8
            data = self.read(1, block)
            data &= ~(1 << bit)
            self.write(data, 1, block)
            i += 1
            address = self.get_inode_address(inode, i)
        offset = 84 + inode * 54 + 18
        self.f.seek(offset)
        self.f.write(('\0' * 36).encode('utf-8'))


    def cd(self, path):
        if path == '/':
            self.f.seek(self.root_offset)
            self.current_offset = self.root_offset
            self.current_path = path
            return self.current_offset
        if path == '..':
            return self.cd(self.current_path[:self.current_path.rstrip('/').rfind('/')+1])
        dirs = path.strip('/').split('/')
        offset = self.root_offset
        for i in range(0, len(dirs)):
            offset = self.find_file_offset(offset, dirs[i])
        if offset != -1:
            self.current_offset = offset
            self.f.seek(offset)
            self.current_path = path
            return self.current_offset
        else:
            return -1


    def access(self, name, action, dir):
        if self.current_user == 'root':
            return 1
        if dir == 1:
            if self.current_path != '/':
                inode = self.read(4, self.current_offset + 28)
                offset = 84 + inode * 54
            else:
                offset = 84
            inode = self.read(4, self.current_offset + 28)
            fuid = self.read(1, 84 + inode * 54 + 1)
        elif dir == 0:
            inode = self.read(4, self.find_file_offset(self.current_offset, name) + 28)
            offset = 84 + inode * 54
            fuid = self.get_file_uid(name)

        attributes = self.read(1, offset)
        if action == 'r':
            if fuid == self.get_uid(self.current_user) and attributes & (1 << 3) != 0 or fuid != self.get_uid(self.current_user) and attributes & (1 << 1) != 0:
                return 1
            else:
                return -1
        elif action == 'w':
            if fuid == self.get_uid(self.current_user) and attributes & (1 << 2) != 0 or fuid != self.get_uid(self.current_user) and attributes & (1 << 0) != 0:
                return 1
            else:
                return -1


    def chmod(self, attributes, name):
        inode = self.read(4, self.find_file_offset(self.current_offset, name) + 28)
        offset = 84 + inode * 54
        at = self.read(1, offset)
        for i in range(4):
            if attributes[i] == '1':
                at |= (1 << 3 - i)
            else:
                at &= ~(1 << 3 - i)
        self.write(at, 1, offset)


    def get_attributes(self, file_offset):
        file_offset += 28
        inode = self.read(4, file_offset)
        offset = 84 + inode * 54
        attributes = self.read(1, offset)
        offset += 1
        user_id = self.read(1, offset)
        attributes_str = ''
        for i in range(4, -1, -1):
            attributes_str += '1' if attributes & (1 << i) != 0 else '0'
        return attributes_str


    def get_file_uid(self, file_name):
        file_offset = self.find_file_offset(self.current_offset, file_name)
        file_offset += 28
        inode = self.read(4, file_offset)
        offset = 84 + inode * 54 + 1
        user_id = self.read(1, offset)
        return user_id


    def get_user(self, uid):
        inode = self.read(4, self.users_offset + 28)
        j = 0
        address = self.get_inode_address(inode, j)
        a = ''
        while address != 0:
            self.f.seek(address)
            while uid != a and self.read(1, address) != '':
                a = self.read(1, address)
                if a == uid:
                    self.f.seek(address+1)
                    return self.f.read(15).decode('utf-8')
                else:
                    address += 48
                    self.f.seek(address)
            j += 1
            address = self.get_inode_address(inode, j)
        return -1


    def get_uid(self, user):
        user += '\0' * (15 - len(user))
        inode = self.read(4, self.users_offset + 28)
        j = 0
        address = self.get_inode_address(inode, j)
        a = ''
        while address != 0:
            self.f.seek(address+1)
            while user != a and self.f.read(15).decode('utf-8') != '':
                self.f.seek(address+1)
                a = self.f.read(15).decode('utf-8')
                if a == user:
                    return self.read(1, address)
                else:
                    address += 48
                    self.f.seek(address+1)
            j += 1
            address = self.get_inode_address(inode, j)
        return -1


    def get_inode_address(self, inode, n):
        if n <= 9:
            offset = 84 + inode * 54 + 14
            address = self.read(4, offset + 4 * n)
            return address
        else:
            return 0


    def find_free_block(self):
        number = 0
        new_offset = 35
        while new_offset != 67:
            data = self.read(1, new_offset)
            for i in range(8):
                if (data & (1 << i)) == 0:
                    number = (new_offset - 35)*8 + i
                    data |= (1 << i)
                    self.write(data, 1, new_offset)
                    return number
            new_offset += 1


    def find_free_inode(self):
        number = 0
        new_offset = 67
        while new_offset != 84:
            data = self.read(1, new_offset)
            for i in range(8):
                if (data & (1 << i)) == 0:
                    number = (new_offset - 67)*8 + i
                    data |= (1 << i)
                    self.write(data, 1, new_offset)
                    return number
            new_offset += 1


    def create_inode(self, attributes, uid):
        current_inode = self.find_free_inode()
        current_block = self.find_free_block()
        date = int(time.time())
        offset = 84 + current_inode*54
        size = 0
        block_count = 1
        self.write(attributes, 1, offset)
        offset += 1
        self.write(uid, 1, offset)
        offset += 1
        self.write(size, 4, offset)
        offset += 4
        self.write(date, 4, offset)
        offset += 4
        self.write(block_count, 4, offset)
        offset += 4
        self.write(current_block*4096, 4, offset)
        self.f.seek(offset+4)
        self.f.write(('\0' * 36).encode('utf-8'))
        return current_inode
