from connectionclass import Connection
from connectionclass import Packet
import pickle
import matplotlib.pyplot as plt

# load_data
with open("sorted.dat", "rb") as f:
    connections = pickle.load(f)


example_addr = "2a00:1450:400c:c04::65"

# late april

# "104.82.239.15"

#test6

    # "31.13.90.2"      # many reorderings, possible negative window error

    # "52.108.240.14"

    # "13.32.67.68" # largest IW, around 20 MSS

    # "52.119.161.208" # small MSS

    # "52.224.109.124"

    # "52.31.28.248"

    # "176.32.98.189"

def plot_connection(address):
    length = []   # temporary lists for individual connections
    t_length = []
    rtt = []
    t_rtt = []
    seq = []
    t_seq = []
    seq2 = []
    t_seq2 = []
    ack = []
    t_ack = []
    sack = []
    t_sack = []
    fin = []
    t_fin = []
    window = []
    t_window = []
    tput = []
    t_tput = []
    syn = []
    t_syn = []
    cipher_change = []
    t_cipher_change = []
    for c in connections:
        if c.destination == address:
            tput = c.throughput
            t_tput = c.throughput_time_n
            for p in c.arrived_packets:
                if hasattr(p, "length"):
                    length.append(p.length)
                    t_length.append(p.connection_timestamp)
                if hasattr(p, "rtt"):
                    rtt.append(p.rtt)
                    t_rtt.append(p.connection_timestamp)
                if hasattr(p, "seq"):
                    seq.append(p.seq)
                    t_seq.append(p.connection_timestamp)
                if hasattr(p, "fin"):
                    fin.append(0)
                    t_fin.append(p.connection_timestamp)
                if hasattr(p, "syn"):
                    syn.append(0)
                    t_syn.append(p.connection_timestamp)
                if hasattr(p, "cipher_change"):
                    if p.cipher_change == 1:
                        cipher_change.append(-100)
                        t_cipher_change.append(p.connection_timestamp)
                # if hasattr(p, "ack"):
                #     ack.append(p.ack)
                #     t_ack.append(p.connection_timestamp)
            for p in c.sent_packets:
                if hasattr(p, "connection_timestamp"):
                    if hasattr(p, "ack"):
                        ack.append(p.ack)
                        t_ack.append(p.connection_timestamp)
                    if hasattr(p, "sack"):
                        sack.append(0)
                        t_sack.append(p.connection_timestamp)
                    if hasattr(p, "window"):
                        window.append(p.window)
                        t_window.append(p.connection_timestamp)
                    if hasattr(p, "seq"):
                        seq2.append(p.seq)
                        t_seq2.append(p.connection_timestamp)
                    if hasattr(p, "syn"):
                        syn.append(0)
                        t_syn.append(p.connection_timestamp)
        # if c.source == address:
        #     fig, ax = plt.subplots()
        #     plt.plot(c.burst_time, c.burst, 'o-', label="Throughput")

    fig, ax = plt.subplots()
    plt.plot(t_length, length, 'o-', label="")
    plt.plot((-100, t_length[-1]), (1220, 1220), label="1220 B, largest segments received from server")
    plt.plot((-100, t_length[-1]), (1440, 1440), label="1440 B, MSS announced by client")
    locs, labels = plt.yticks(range(0, 1600, 100))
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.title("Segment Length consistently lower that MSS")
    plt.ylabel("Segment size (Bytes)")
    plt.xlabel("Time since connection started (ms)")
    # fig, ax = plt.subplots()
    # plt.plot(t_rtt, rtt, 'o-')
    # plt.title("Round-Trip Time")
    # plt.ylabel("RTT (ms)")
    # plt.xlabel("Time since connection started (ms)")
    fig, ax = plt.subplots()
    plt.plot(t_seq, seq, 'o-', label="Sequence received at client")
    plt.plot(t_syn, syn, 'x')
    plt.plot(t_fin, fin, 'x')
    plt.plot(t_cipher_change, cipher_change, 'o')
    plt.plot(t_sack, sack, 'x', color='r')
    plt.title("Sequence Number")
    plt.ylabel("Sequence received (Bytes)")
    plt.xlabel("Time since connection started (ms)")
    # fig, ax = plt.subplots()
    # plt.plot(t_seq2, seq2, 'o-', label="Sequence received at client")
    # plt.plot(t_fin, fin, 'x')
    # plt.plot(t_sack, sack, 'x', color='r')
    # plt.title("Sequence Number")
    # plt.ylabel("Sequence sent (Bytes)")
    # plt.xlabel("Time since connection started (ms)")
    # plt.plot([970, 980], [0, 0], 'r-', lw=5, label="_not")    # fb lines
    # plt.plot([987, 996], [30000, 30000], 'r-', lw=5, label="_not")
    # plt.plot([133, 151], [0, 0], 'r-', lw=5, label="_not")    # yahoo lines
    # plt.plot([160, 175], [10000, 10000], 'r-', lw=5, label="_not")
    # plt.plot([189, 200], [30000, 30000], 'r-', lw=5, label="_not")
    # plt.plot([229, 247], [60000, 60000], 'r-', lw=5, label="_not")
    # fig, ax = plt.subplots()
    # plt.plot(t_ack, ack, 'o-', label="ACKs sent by client")
    # plt.plot(t_sack, sack, 'x', color='r')
    # plt.title("ACKed sequence")
    # plt.ylabel("Sequence Acknowledged (Bytes)")
    # plt.xlabel("Time since connection started (ms)")
    # fig, ax = plt.subplots()
    # plt.plot(t_window, window, 'o-', label="Client's advertised window")
    # plt.title("Advertised Window size")
    # plt.ylabel("Window size (Bytes)")
    # plt.xlabel("Time since connection started (ms)")
    # plt.plot(t_tput, tput, 'o-')
    # plt.title("Throuhgput")
    # plt.ylabel("Mbps")
    # plt.title("Burst Size limited by Window")
    # plt.ylabel("Sequence Received/Acknowledged (Bytes)")
    # plt.xlabel("Time since connection started (ms)")
    # plt.plot([4186, 4199], [360000, 360000], label="Time Gap")
    # ax.legend()


# use the facebook one to discuss rtt gaps
# try to use beatiful soup to open all links and picture etc

# connectionclass.sort_packets()
# connectionclass.write_longest_connections()
# connectionclass.calculate_throughput()
# connectionclass.burst_size()


plot_connection(example_addr)

plt.show()
