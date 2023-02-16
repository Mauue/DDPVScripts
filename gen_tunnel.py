import random

space_file = "%s\%s.space"
tunnel_file = "%s\%s.%s.tunnel"

space = {}

space_size = 0

tunnel = []

devices = []


def read_space(network):
    global space_size
    global devices
    with open(space_file % (network, network), mode="r", encoding="utf-8") as f:
        s = f.readline()
        while s:
            token = s.split(" ")
            device = token[0]
            ip = int(token[1])
            prefix = int(token[2])
            space[device] = (ip, prefix)
            space_size = prefix
            s = f.readline()
    devices = list(space.keys())


def gen_tunnel():
    t_entry, t_exit, t_packet = random.sample(devices, k=3)
    ip_exit = space[t_exit]
    ip_packet = space[t_packet]
    match = ip_exit[0] + random.getrandbits(32-ip_exit[1])
    target = ip_packet[0] + random.getrandbits(32-ip_packet[1])
    tunnel.append((t_entry, t_exit, match, target, 32))


def gen_tunnel_batch(count):
    for _ in range(count):
        gen_tunnel()


def output(filename):
    with open(filename, mode="w", encoding="utf-8") as f:
        for i in tunnel:
            f.write("%s %s %s %s %s\n" % i)


if __name__ == "__main__":
    network = "BtNorthAmerica"
    read_space(network)
    # print(space)
    num = 50
    gen_tunnel_batch(num)
    output(tunnel_file % (network, network, num))

