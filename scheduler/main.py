queue0 = []
queue1 = []
count = 0


class Process:
    def __init__(self, pri, ni, state, cpu):
        global count
        self.pid = count
        self.pri = pri
        self.ni = ni
        self.cpu = cpu
        self.state = state
        self.io = 3
        count += 1

    def set_ni(self, ni):
        self.ni += ni

    def set_state(self, state):
        self.state = state

    def decr_io(self):
        self.io -= 1

    def decr_cpu(self):
        self.cpu -= 1


def run_command(queue):
    input_line = input()

    if input_line == '\n':
        return

    command = input_line.split()

    if len(command) < 2 or len(command) > 4:
        return

    if command[0] == 'kill' and len(command) == 2:
        try:
            pid = int(command[1])
        except:
            return

        for p in queue:
            if p.pid == pid:
                queue.remove(p)

    if command[0] == 'renice' and len(command) == 3:
        try:
            pid = int(command[1])
            ni = int(command[2])
        except:
            return

        for p in queue0:
            if p.pid == pid:
                p.set_ni(ni)
        for p in queue1:
            if p.pid == pid:
                p.set_ni(ni)

    if command[0] == 'add' and len(command) == 4:
        try:
            pri = int(command[1])
            ni = int(command[2])
            cpu = int(command[3])
        except:
            return

        if pri == 0 and cpu > 0:
            queue0.append(Process(0, ni, 'Г', cpu))
        elif pri == 1 and cpu > 0:
            queue1.append(Process(1, ni, 'Г', cpu))


def run_queue0(last):
    quant = 4
    current = last
    current += 1

    if len(queue0) == 0:
        return -1

    if current >= len(queue0):
        current = 0

    while queue0[current].state == 'З':
        current += 1
        if current == len(queue0):
            current = 0
            if queue0[current].state == 'З':
                return -1

    for j in range(0, quant):
        for i, p in enumerate(queue0):
            if p.state == 'З':
                if current == i:
                    current += 1
                if current == len(queue0):
                    current = 0
                continue

            if p.state == 'Г' and current == i:
                p.set_state('И')
                p.decr_cpu()
            elif p.state == 'И' and current == i:
                p.decr_cpu()
            elif p.state == 'О':
                p.decr_io()
                if p.io == 0:
                    p.set_state('З')

                '''/*current += 1
                if current == len(queue0):
                    current = 0'''

            if (p.state == 'Г' or p.state == 'И') and p.cpu == 0:
                p.set_state('О')
                current += 1
                if current == len(queue0):
                    current = 0

        print(f'Очередь 0 (RR), такт {j + 1}:')
        for p in queue0:
            print(f'PID: {p.pid}, NI: {p.ni}, STATE: {p.state}, CPU: {p.cpu}, IO: {p.io}')
            if p.state == 'И':
                p.set_state('Г')

    return current


def run_queue1(last):
    current = last

    if len(queue1) == 0:
        return -1

    if current >= len(queue1):
        current = 0

    while queue1[current].state == 'З':
        current += 1
        if current == len(queue1):
            current = 0
            if queue1[current].state == 'З':
                return -1

    print("Очередь 1 (FCFS):")
    for i, p in enumerate(queue1):
        if p.state == 'Г' and current == i:
            p.set_state('И')
            p.decr_cpu()
        elif p.state == 'И' and current == i:
            p.decr_cpu()

        if p.state == 'О':
            p.decr_io()
            if p.io == 0:
                p.set_state('З')

        if (p.state == 'Г' or p.state == 'И') and p.cpu == 0:
            p.set_state('О')
            current += 1
            if current == len(queue1):
                current = 0

        print(f'PID: {p.pid}, NI: {p.ni}, STATE: {p.state}, CPU: {p.cpu}, IO: {p.io}')

    return current


def is_finished(queue):
    for p in queue:
        if p.state != 'З':
            return True
    return False


queue0.append(Process(0, 0, 'Г', 24))
queue0.append(Process(0, 0, 'Г', 16))
queue0.append(Process(0, 0, 'Г', 22))
queue1.append(Process(1, 2, 'Г', 16))
queue1.append(Process(1, 1, 'Г', 18))
queue1.append(Process(1, -5, 'Г', 4))

while is_finished(queue0) or is_finished(queue1):
    if is_finished(queue0):
        print('\n' + '*'*39 + '\n')
        pid = run_queue0(-1)
        run_command(queue0)
        print('\n' + '*'*39 + '\n')
        while pid != -1:
            if queue0[0].cpu == 7:
                a = 0
                pass
            pid = run_queue0(pid)
            run_command(queue0)
            print('\n' + '*'*39 + '\n')
            continue

    if is_finished(queue1):
        queue1 = sorted(queue1, key=lambda process: process.ni)
        print('\n' + '*'*39 + '\n')
        pid = run_queue1(0)
        run_command(queue1)
        print('\n' + '*'*39 + '\n')
        while pid != -1:
            if is_finished(queue0):
                break
            pid = run_queue1(pid)
            run_command(queue1)
            print('\n' + '*'*39 + '\n')
            continue
