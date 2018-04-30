import csv
import pickle

# cd desktop\wiresharkscripts


input_file = "results.txt"




# IPv4, IPv6, Ports, TCP len, MSS, RTT, SYN, time, rwin, seq, ack, fin, cipher, sack
#    0   1       2     3       4    5    6    7     8    9    10    11    12    13
class Packet:
    def __init__(self, row, c):
        if row[3]:
            self.length = int(row[3])
        if row[4]:
            self.mss = int(row[4])
        if row[5]:
            self.rtt = float(row[5]) * 1000
        if row[6] == "1":
            self.syn = True
        # all packets should have timestamp
        self.timestamp = round(float(row[7]) * 1000, 3)
        self.connection_timestamp = self.timestamp - c.connection_start
        if row[8]:
            self.rec_window = int(row[8])
        try:
            if row[9]:
                self.seq = int(row[9])
        except ValueError:
            print(row)
        if row[10] == "1":
            self.ack = True
        if row[11] == "1":
            self.fin = True
        if row[12] == "1":
            self.cipher_change = 1
        if row[13]:        # sack if there has been a loss in transmission
            self.sack = 1





class Connection:
    # average throughput
    def __init__(self, x, ip):
        self.IP = ip
        if ip == 4:
            IPv4 = x[0].split(" ")
            self.source = IPv4[0]
            self.destination = IPv4[1]
        elif ip == 6:
            IPv4 = x[1].split(" ")
            self.source = IPv4[0]
            self.destination = IPv4[1]


        if x[2]:
            ports = x[2].split(" ")
            self.source_port = ports[0]
            self.destination_port = ports[1]

        self.sent_packets = []
        self.arrived_packets = []

        if x[7]:
            self.connection_start = float(x[7]) * 1000 # ms

        self.burst = []
        self.burst_time = []

        self.throughput_time = []
        self.throughput_time_n =[]
        self.throughput = []

        self.RTprop_time = []
        self.est_RTprop = []
        self.RTprop_list = []
        self.est_btlBW = []
        self.btlBW_list = []

        self.BDP_time = []
        self.Bandwidth_delay_product =[]

        self.last_pkt = 0

        self.wavg = 0   # used for estimating congestion window size




source_dest = []    # list of lists of ip addresses
connections = []    # list of Connection objects


def save_data(data):
    with open("sorted.dat", "wb") as f:
        pickle.dump(data, f)


# generator to read large files without loading everything
def read_line_by_line (file_path):
    with open (file_path, 'r') as f:
        for line in f:
            yield line

# create objects with all their values
def sort_packets():
    # search through the text file of all captured packets
    for line in read_line_by_line(input_file):
        # create a list from the string
        row = line.split(",")
        if row[0]:
            IP = 4
            IPv4 = row[0].split(" ")
            IP_combination = [IPv4[0], IPv4[1]]
            if len(IPv4) > 2:
                continue
        elif row[1]:
            IP = 6
            IPv6 = row[1].split(" ")
            IP_combination = [IPv6[0], IPv6[1]]
        else:
            continue

        inverse_IP = [IP_combination[1], IP_combination[0]]

        # if connection doesn't exist, create it
        if IP_combination not in source_dest:
            if inverse_IP not in source_dest:
                source_dest.append(IP_combination)
                connections.append(Connection(row, IP))
        # find which connection this packet belongs to
        for c in connections:
            if IP_combination[0] == c.source and IP_combination[1] == c.destination:
                c.sent_packets.append(Packet(row, c))
            elif IP_combination[1] == c.source and IP_combination[0] == c.destination:
                c.arrived_packets.append(Packet(row, c))


# # calculate throughput etc
# def calculate_throughput():
#     for c in connections:
#         for p in c.packets:
#             if hasattr(p, 'timestamp') and hasattr(p, 'length') and hasattr(p, 'connection_timestamp'):
#                 # sum of lengths of packets sent during delta_t
#                 delta_t = 1
#                 temp_length_sum = 0
#                 for pp in c.packets:
#                     if hasattr(pp, 'timestamp'):
#                         if (pp.timestamp + delta_t) > p.timestamp and pp.timestamp <= p.timestamp:
#                             temp_length_sum += pp.length
#                 delta_L = temp_length_sum
#                 c.throughput_time.append(p.timestamp)
#                 c.throughput_time_n.append(p.connection_timestamp)
#                 c.throughput.append(delta_L)  # Bytes p s
#                 if hasattr(p, 'rtt'):
#                     c.btlBW_list.append(c.throughput[-1] / 8)   # bytes
#                     c.est_btlBW.append(max(c.btlBW_list))
#                     c.RTprop_list.append(p.rtt)
#                     c.est_RTprop.append(min(c.RTprop_list))
#                     c.RTprop_time.append(p.timestamp)
#
#                     c.BDP_time.append(p.timestamp)
#                     c.Bandwidth_delay_product.append(c.est_RTprop[-1] * c.est_btlBW[-1])    #Mbits
#                 elif c.est_RTprop and c.est_btlBW:
#                     c.BDP_time.append(p.timestamp)
#                     c.Bandwidth_delay_product.append(c.est_RTprop[-1] * c.est_btlBW[-1])
#
#
#
#
#
# # most common ip address is this computer
# def find_most_used_ip(list_of_connections=connections):
#     counts = dict()
#     for i in [c.source for c in list_of_connections]:
#         if i in counts:
#             counts[i] += 1
#         else:
#             counts[i] = 1
#     maxcount = max(counts.values())
#     for ip, count in counts.items():
#         if count == maxcount:
#             return ip
#
#
#
#
# def write_longest_connections():
#     with open("long_connections.txt", "w") as txtfile:
#         print("by number of packets")
#         txtfile.write("by number of packets\n")
#         for c in connections:
#             fin_pkt = 0
#             local_max = 0
#             for num_pkts, p in enumerate(c.packets):
#                 if hasattr(p, "fin"):
#                     fin_pkt = num_pkts
#                 pkts_since_fin = num_pkts - fin_pkt
#                 if pkts_since_fin > local_max:
#                     local_max = pkts_since_fin
#             if local_max > 100:
#                 print(c.source, local_max)
#                 txtfile.write(c.source + "    " + str(local_max) + "\n")
#         print("by time")
#         txtfile.write("by time\n")
#         for c in connections:
#             fin_time = 0
#             local_max = 0
#             for p in c.packets:
#                 if hasattr(p, "connection_timestamp"):
#                     if hasattr(p, "fin"):
#                         fin_time = p.connection_timestamp
#                     time_since_fin = p.connection_timestamp - fin_time
#                 if time_since_fin > local_max:
#                     local_max = time_since_fin
#             if local_max > 500:
#                 print(c.source, local_max)
#                 txtfile.write(c.source + "    " + str(local_max))
#                 txtfile.write("\n")
#
#
#


if __name__ == "__main__":
    # sort_packets()
    # print("packets sorted!")
    # calculate_throughput()
    # print("throughput sorted!")
    # find_most_used_ip()
    # print("most used ip found!")
    # write_longest_connections()
    # print("packets sorted!")

    # save sorted data
    sort_packets()
    print("sorted")
    save_data(connections)
    print("saved")




#
