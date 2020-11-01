import subprocess
import copy
import os


def prepare_vm(vm_name, label, snapshot, username, password, path=""):
    vm = None

    if vm_name == "virtualbox":
        if not path:
            path = "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe"
        vm = VirtualBox(path, label, snapshot, username=username, password=password)
    elif vm_name == "vmware":
        if not path:
            path = "C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmrun.exe"
        vm = VMWare(path, label, snapshot, username=username, password=password)
    else:
        return None

    vm.restore()
    vm.start()

    return vm


def finish_vm(vm):
    vm.stop()


def execute(command):
    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            close_fds=True,
        )
        stdout, err = proc.communicate()
        proc.wait()
        if err:
            print("command: " + str(command))
            print("error: " + err)
        return stdout, err
    except Exception as e:
        print("command: " + str(command))
        print(e)
    return "error", "error"


class VirtualMachine:
    path = ""
    mode = ""
    label = ""
    snapshot = ""
    username = ""
    password = ""
    # vm control
    start_cmd = []
    restore_cmd = []
    stop_cmd = []
    # file
    copy_file_host_to_guest_cmd = []
    copy_file_guest_to_host_cmd = []
    mkdir_cmd = []
    list_file = []
    # exec
    exec_cmd = []
    # network
    get_ip_addr_cmd = []
    # other
    list_vm_cmd = []

    def __init__(self, path, label, snapshot, username, password):
        self.path = path
        # virtualbox: gui or headless
        # vmware: gui or nogui
        self.mode = "gui"
        self.label = label
        self.snapshot = snapshot
        self.username = username
        self.password = password

    # vm control
    def start(self):
        output, err = execute(self.start_cmd)
        return output, err

    def stop(self):
        output, err = execute(self.stop_cmd)
        return output, err

    def restore(self):
        output, err = execute(self.restore_cmd)
        return output, err

    # file
    def copy_file_host_to_guest(self, src_path, dst_path):
        src_path = src_path.replace("/", "\\")
        dst_path = dst_path.replace("/", "\\")

        cmd = copy.copy(self.copy_file_host_to_guest_cmd)
        cmd.append(src_path)
        cmd.append(dst_path)
        output, err = execute(cmd)
        return output, err

    def copy_file_guest_to_host(self, src_path, dst_path):
        src_path = src_path.replace("/", "\\")
        dst_path = dst_path.replace("/", "\\")

        cmd = copy.copy(self.copy_file_guest_to_host_cmd)
        cmd.append(src_path)
        cmd.append(dst_path)
        output, err = execute(cmd)
        return output, err

    def mkdir(self, target_path):
        target_path = target_path.replace("/", "\\")

        cmd = copy.copy(self.mkdir_cmd)
        cmd.append(target_path)
        output, err = execute(cmd)
        return output, err

    # exec
    def exec(self, image_path, arg_list):
        image_path = image_path.replace("/", "\\")

        cmd = copy.copy(self.exec_cmd)
        cmd.append(image_path)
        cmd.extend(arg_list)
        output, err = execute(cmd)
        return output, err

    # network
    def get_ip_addr(self):
        output, err = execute(self.get_ip_addr_cmd)

        ip_addr = output.split(" ")[-1].replace("\n", "")

        return ip_addr

    # other
    def list_vm(self):
        output, err = execute(self.list_vm_cmd)

        vm_labels = []

        for line in output.split("\n"):
            if '"' not in line:
                continue

            label = line.split('"')[1]

            vm_labels.append(label)

        return vm_labels


class VirtualBox(VirtualMachine):
    def __init__(self, path, label, snapshot, username, password):
        super().__init__(path, label, snapshot, username=username, password=password)
        # vm control
        self.start_cmd = [self.path, "startvm", self.label, "--type", self.mode]
        self.stop_cmd = [self.path, "controlvm", self.label, "poweroff"]
        self.restore_cmd = [self.path, "snapshot", self.label, "restore", self.snapshot]
        # file
        self.copy_file_host_to_guest_cmd = [
            self.path,
            "guestcontrol",
            self.label,
            "--username",
            self.username,
            "--password",
            self.password,
            "copyto",
        ]
        self.copy_file_guest_to_host_cmd = [
            self.path,
            "guestcontrol",
            self.label,
            "--username",
            self.username,
            "--password",
            self.password,
            "copyfrom",
        ]
        self.mkdir_cmd = [
            self.path,
            "guestcontrol",
            self.label,
            "--username",
            self.username,
            "--password",
            self.password,
            "mkdir",
            "--parents",
        ]
        self.list_file = []
        # exec
        self.exec_cmd = [
            self.path,
            "guestcontrol",
            self.label,
            "--username",
            self.username,
            "--password",
            self.password,
            "run",
        ]
        # network
        self.get_ip_addr_cmd = [
            self.path,
            "guestproperty",
            "get",
            self.label,
            "/VirtualBox/GuestInfo/Net/0/V4/IP",
        ]
        # other
        self.list_vm_cmd = [self.path, "list", "vms"]


class VMWare(VirtualMachine):
    def __init__(self, path, label, snapshot, username, password):
        super().__init__(path, label, snapshot, username=username, password=password)
        # vm control
        self.start_cmd = [self.path, "start", self.label, self.mode]
        self.stop_cmd = [self.path, "stop", self.label, "hard"]
        self.restore_cmd = [self.path, "revertToSnapshot", self.label, self.snapshot]
        # file
        self.copy_file_host_to_guest_cmd = [
            self.path,
            "-gu",
            self.username,
            "-gp",
            self.password,
            "copyFileFromHostToGuest",
            self.label,
        ]
        self.copy_file_guest_to_host_cmd = [
            self.path,
            "-gu",
            self.username,
            "-gp",
            self.password,
            "copyFileFromGuestToHost",
            self.label,
        ]
        self.mkdir_cmd = [
            self.path,
            "-gu",
            self.username,
            "-gp",
            self.password,
            "createDirectoryInGuest",
            self.label,
        ]
        self.list_file = [
            self.path,
            "-gu",
            self.username,
            "-gp",
            self.password,
            "listDirectoryInGuest",
            self.label,
        ]
        # exec
        self.exec_cmd = [
            self.path,
            "-gu",
            self.username,
            "-gp",
            self.password,
            "runProgramInGuest",
            self.label,
            "-interactive",
        ]
        # network
        self.get_ip_addr_cmd = [self.path, "getGuestIPAddress", self.label]
        # other
        self.list_vm_cmd = []

    def copy_file_guest_to_host(self, src_path, dst_path):
        src_path = src_path.replace("/", "\\")
        dst_path = dst_path.replace("/", "\\")

        file_list = []
        if src_path[-1] == "/" or src_path[-1] == "\\":
            list_file_cmd = copy.copy(self.list_file)
            list_file_cmd.append(src_path)
            output, err = execute(list_file_cmd)
            if len(output.split("\n")) > 1:
                output = output.replace("\r", "")
                for file_name in output.split("\n")[1:]:
                    if len(file_name) <= 0:
                        continue
                    file_list.append(src_path + file_name)
        else:
            file_list.append(src_path)

        output = ""
        err = ""
        for file_path in file_list:
            cmd = copy.copy(self.copy_file_guest_to_host_cmd)
            cmd.append(file_path)
            cmd.append(dst_path + os.path.basename(file_path))
            output, err = execute(cmd)
        return output, err
