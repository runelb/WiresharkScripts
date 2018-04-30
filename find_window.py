from sorting import Connection
from sorting import Packet
import pickle
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# load_data
with open("sorted.dat", "rb") as f:
    connections = pickle.load(f)



temp_ip = "54.239.31.69"

num_windows = 0
dec_connection = 0
too_short_connection = 0
bad_window = 0
connections_with_IW = 0

mss_same = 0
mss_diff = 0

TLS_IP4 = 0
TLS_IP6 = 0
_IP4 = 0
_IP6 = 0

max_wind = []
max_wind_b = []


HTTPS_IW = []
HTTP_IW = []
HTTPS_IW2 = []
HTTP_IW2 = []
Strue_IW = []
Strue_IW2 = []
true_IW = []
true_IW2 = []


HTTPS_6IW = []
HTTP_6IW = []
HTTPS_6IW2 = []
HTTP_6IW2 = []
Strue_6IW = []
Strue_6IW2 = []
true_6IW = []
true_6IW2 = []

total_IW = []
all_HTTP_IW = []
all_HTTPS_IW = []
all_v4_IW = []
all_v6_IW = []

total_IW2 = []
all_HTTP_IW2 = []
all_HTTPS_IW2 = []
all_v4_IW2 = []
all_v6_IW2 = []



def find_syn_ack(c):
    syn_pkts = []
    syn_ack_pkts = []
    TLS_start = []
    uses_TLS = False

    for p in c.arrived_packets:
        if hasattr(p, "syn") and hasattr(p, "ack"):
            syn_ack_pkts.append(p)
    for p in c.sent_packets:
        if hasattr(p, "syn"):
            syn_pkts.append(p)
        if hasattr(p, "cipher_change"):
            if p.cipher_change == 1:
                TLS_start.append(p.timestamp)
                uses_TLS = True


    if len(syn_pkts) == 0 or len(syn_ack_pkts) == 0:    # no handshake, connection useless
        return [], [], [], uses_TLS

    none_found = False
    if len(syn_ack_pkts) < len(syn_pkts):
        while len(syn_ack_pkts) < len(syn_pkts):   # delete excess syn pkts
            for s in range(len(syn_ack_pkts)):
                if syn_ack_pkts[s].timestamp > syn_pkts[s + 1].timestamp:
                    del syn_pkts[s]
                    break
                else:
                    none_found = True
            if none_found:      # if no overlapping syn found above, the extra syn must be at the end
                del syn_pkts[-1]

    return syn_pkts, syn_ack_pkts, TLS_start, uses_TLS


def find_RTT(syn_pkts, syn_ack_pkts, IP):
    RTT = []
    avg_RTT = 0
    global bad_window
    for i in range(len(syn_pkts)):
        syn_time = syn_pkts[i].timestamp
        syn_ack_time = syn_ack_pkts[i].timestamp
        if syn_ack_time - syn_time < 0:
            bad_window += 1
            continue
        RTT.append(syn_ack_time - syn_time)
        avg_RTT += (syn_ack_time - syn_time)

    # replace values too far outside the range          # maybe better to just insert NaN and ignore??
    if RTT:
        avg_RTT = avg_RTT / len(RTT)
        for r in RTT:
            if r < avg_RTT / 2:
                # print("replacing rtt")
                r = avg_RTT
            if r > avg_RTT * 2:
                r = avg_RTT
                # print("replacing rtt")

    return RTT, avg_RTT


with open("window_data.txt", "w") as f:
    for c in connections:
        syn_pkts = []
        syn_ack_pkts = []
        TLS_start = []

        RTT = []
        IW = []
        IW2 = []
        MSS = []
        MSS2 = []

        RTT_for_IW = []


        syn_pkts, syn_ack_pkts, TLS_start, uses_TLS = find_syn_ack(c)

        if len(syn_pkts) == 0 or len(syn_ack_pkts) == 0:    # no handshake, connection useless
            too_short_connection += 1
            continue

        RTT, avg_RTT = find_RTT(syn_pkts, syn_ack_pkts, c.destination)


        # after each separate handshake, find each of their windows
        recd_packets = c.arrived_packets
        for start_index in range(len(syn_ack_pkts)):    # loop through each re-start to find their windows
            if uses_TLS:
                looking_for_TLS = True
                looking_for_window_start = False
            else:
                looking_for_TLS = False
                looking_for_window_start = True

            looking_for_window_end = False
            last_syn = False

            syn_ack_time = syn_ack_pkts[start_index].timestamp
            try:
                next_syn_time = syn_pkts[start_index + 1].timestamp
            except IndexError:
                last_syn = True

            for i in range(len(recd_packets)):          # loop through received packets to find the initial window
                # ignore earlier transmissions
                if recd_packets[i].timestamp < syn_ack_time:
                    continue
                # ignore later transmissions
                if not last_syn:
                    if recd_packets[i].timestamp > next_syn_time:
                        break
                if hasattr(recd_packets[i], "fin"):
                    break
                if not hasattr(recd_packets[i], "length") or not hasattr(recd_packets[i], "seq"):
                    continue

                if looking_for_TLS:
                    if recd_packets[i].timestamp > syn_ack_time:
                        if hasattr(recd_packets[i], "cipher_change"):
                            if recd_packets[i].cipher_change == 1:
                                TLS_end = recd_packets[i]
                                try:
                                    alt_RTT = TLS_end.timestamp - TLS_start[start_index]
                                    if alt_RTT < RTT[start_index]:
                                        RTT[start_index] = alt_RTT
                                except IndexError:
                                    pass
                                looking_for_TLS = False
                                looking_for_window_start = True
                if looking_for_window_start:
                    # found if next two pkts close in time and carrying data           # the starting point of the window's sequence
                    try:
                        if recd_packets[i + 1].timestamp - recd_packets[i].timestamp < RTT[start_index] * 1/10:      # pkts in window very close, perhaps shorter time?
                            if hasattr(recd_packets[i + 1], "length") and hasattr(recd_packets[i], "length"):
                                if recd_packets[i + 1].length > 1 and recd_packets[i].length > 1:
                                    wind_start_index = i
                                    wind_start = recd_packets[wind_start_index]                # next packet is in the window
                                    start_seq = recd_packets[i].seq                 # window data starts from here
                                    looking_for_window_start = False
                                    looking_for_window_end = True
                    except IndexError:      # if no packet two steps ahead, impossible to find initial window
                        bad_window += 1
                        break
                if looking_for_window_end:
                    try:
                        # if recd_packets[i + 1].timestamp - recd_packets[i].timestamp > RTT[start_index] * 1/10:   # inverted start
                        if recd_packets[i + 1].timestamp > wind_start.timestamp + RTT[start_index] * 1/2:      # this assumes the burst arrives entirely in 1/3 RTT...
                            if hasattr(recd_packets[i + 1], "syn"):     # if the next packet is not in a second burst, but a restart
                                bad_window += 1
                                break
                            if not hasattr(recd_packets[i + 1], "seq"):
                                continue
                            # the final sequence number including ALL data sent in the window, is the first sequence number of the next window
                            end_seq = recd_packets[i + 1].seq

                            # max segment size is the largest  segment sent out of packets in this window
                            try:
                                max_segment_size = max([recd_packets[x].length for x in range(wind_start_index, i + 1)])
                            except AttributeError:
                                max_segment_size = syn_ack_pkts[start_index].mss
                            if max_segment_size == syn_pkts[start_index].mss:
                                mss_same += 1
                            else:
                                mss_diff += 1

                            window_size = end_seq - start_seq
                            window_mss = window_size / syn_pkts[start_index].mss
                            if window_mss < 1:
                                bad_window += 1
                                break
                            window_mss2 = window_size / max_segment_size                # syn_ack_pkts[start_index].mss
                            max_wind.append(window_mss)
                            IW.append(window_mss)
                            IW2.append(window_mss2)
                            MSS.append(syn_pkts[start_index].mss)
                            MSS2.append(max_segment_size)                               # syn_ack_pkts[start_index].mss)
                            RTT_for_IW.append(RTT[start_index])
                            num_windows += 1
                            if uses_TLS:
                                if c.IP == 4:
                                    HTTPS_IW.append(window_mss)
                                    HTTPS_IW2.append(window_mss2)
                                elif c.IP == 6:
                                    HTTPS_6IW.append(window_mss)
                                    HTTPS_6IW2.append(window_mss2)
                            else:
                                if c.IP == 4:
                                    HTTP_IW.append(window_mss)
                                    HTTP_IW2.append(window_mss2)
                                elif c.IP ==6:
                                    HTTP_6IW.append(window_mss)
                                    HTTP_6IW2.append(window_mss2)
                            break
                    except IndexError:     # if end is reached and there are no more packets, IW cannot be read
                        bad_window += 1
                        break

        if HTTPS_IW or HTTP_IW:
            dec_connection += 1


        # only write output if there is IW found
        try:
            avg_IW = sum(IW) / len(IW)
        except ZeroDivisionError:       # if len(IW) == 0, then no useful information
            too_short_connection += 1
            continue
        f.write(c.destination + "\n")
        f.write("average RTT: " + str(avg_RTT) + "\n")
        connections_with_IW += 1
        if uses_TLS:
            all_HTTPS_IW.append(IW[0])
            all_HTTPS_IW2.append(IW2[0])
            if c.IP == 4:
                TLS_IP4 += 1
                all_v4_IW.append(IW[0])
                all_v4_IW2.append(IW2[0])
                f.write("IPv4, HTTPS\n")
                Strue_IW.append(IW[0])
                Strue_IW2.append(IW2[0])
            elif c.IP == 6:
                TLS_IP6 += 1
                all_v6_IW.append(IW[0])
                all_v6_IW2.append(IW2[0])
                f.write("IPv6, HTTPS\n")
                Strue_6IW.append(IW[0])
                Strue_6IW2.append(IW2[0])
        else:
            all_HTTP_IW.append(IW[0])
            all_HTTP_IW2.append(IW2[0])
            if c.IP == 4:
                _IP4 += 1
                all_v4_IW.append(IW[0])
                all_v4_IW2.append(IW2[0])
                f.write("IPv4, HTTP\n")
                true_IW.append(IW[0])
                true_IW2.append(IW2[0])
            elif c.IP ==6:
                _IP6 += 1
                all_v6_IW.append(IW[0])
                all_v6_IW2.append(IW2[0])
                f.write("IPv6, HTTP\n")
                true_6IW.append(IW[0])
                true_6IW2.append(IW2[0])
        total_IW.append(IW[0])
        total_IW2.append(IW2[0])
        f.write("average initial window size over restarted connections: " + str(avg_IW)+ " MSS\n")
        f.write("rounded average initial window size over restarted connections: " + str(round(avg_IW))+ " MSS\n")
        f.write("largest initial window: " + str(max(IW)) + " MSS\n")
        f.write("rounded largest initial window: " + str(round(max(IW))) + " MSS\n")

        f.write("truly initial window RTT: " + str(RTT_for_IW[0]) + "\n")
        f.write("truly initial window size: " + str(IW[0]) + "\n")
        f.write("rounded truly initial window size: " + str(round(IW[0])) + "\n")
        f.write("where MSS = " + str(MSS[0]) + "\n\n")

        f.write("truly initial window size: " + str(IW2[0]) + "\n")
        f.write("rounded truly initial window size: " + str(round(IW2[0])) + "\n")
        f.write("where MSS = " + str(MSS2[0]) + "\n\n\n")





print("maximum window size:")
print(max(max_wind), max(max_wind)/1460, "MSS")


print(num_windows, "windows counted")
print(dec_connection, "connections counted")
print(bad_window, "to small windows")
print(too_short_connection, "too short connections")
print(mss_same, "mss is as announced")
print(mss_diff, "mss different announced")

print(len(all_v4_IW), "ipv4 connections")
print(len(all_v6_IW), "ipv6 connections")
print(len(all_HTTP_IW), "http connections")
print(len(all_HTTPS_IW), "https connections")

print(connections_with_IW, "connections with IW")

print(TLS_IP4, "connections using tls and ipv4")
print(TLS_IP6, "connections using tls and ipv6")
print(_IP4, "connections without tls and ipv4")
print(_IP6, "connections without tls and ipv6")


print(len(connections), "total connections")

range_used = range(30)

lbl = "HTTPS, IPv4", "HTTP, IPv4", "HTTPS, IPv6", "HTTP, IPv6"

ttl = "Distribution of Initial Window (IW) Sizes\n"
ttla = "Distribution of Initial Window (IW) Sizes\nAnnounced MSS"
ttlb = "Distribution of Initial Window (IW) Sizes\nMSS Recorded"

xaxisa = "Initial Window Size (Announced MSS)"
xaxisb = "Initial Window Size (MSS Recorded)"

yaxis = "% of connections using as initial window"

# n, bins, patches = plt.hist((HTTPS_IW, HTTP_IW, HTTPS_6IW, HTTP_6IW), range_used, histtype="bar", label=lbl, density=True)
# locs, labels = plt.xticks(range_used)
# plt.xlabel(xaxisa)
# plt.ylabel(yaxis)
# plt.title(ttl + "\nAnnounced MSS")
# plt.legend()
#
# fig, ax = plt.subplots()
# n, bins, patches = plt.hist((HTTPS_IW2, HTTP_IW2, HTTPS_6IW2, HTTP_6IW2), range_used, histtype="bar", label=lbl, density=True)
# locs, labels = plt.xticks(range_used)
# plt.xlabel(xaxisb)
# plt.ylabel(yaxis)
# plt.title(ttl + "\nMSS Recorded")
# plt.legend()

# all separate, MMSa
fig, ax = plt.subplots()
n, bins, patches = plt.hist((Strue_IW, true_IW, Strue_6IW, true_6IW), range_used, histtype="barstacked", label=lbl, density=True, align='left', edgecolor='k')
locs, labels = plt.xticks(range_used)
plt.xlabel(xaxisa)
plt.ylabel(yaxis)
plt.title(ttla)
plt.legend()

# all separate, MSSb
fig, ax = plt.subplots()
n, bins, patches = plt.hist((Strue_IW2, true_IW2, Strue_6IW2, true_6IW2), range_used, histtype="barstacked", label=lbl, density=True, align='left', edgecolor='k')
locs, labels = plt.xticks(range_used)
plt.xlabel(xaxisb)
plt.ylabel(yaxis)
plt.title(ttlb)
plt.legend()

yrange = []
for y in range(10):
    yrange.append(y/50)

# total MSSa
fig, ax = plt.subplots()
n, bins, patches = plt.hist(total_IW, range_used, histtype="bar", density=True, align='left', edgecolor='k')
locs, labels = plt.xticks(range_used)
locs, labels = plt.yticks(yrange)
plt.xlabel(xaxisa)
plt.ylabel(yaxis)
plt.title(ttla)
plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()])

# total MSSb
fig, ax = plt.subplots()
n, bins, patches = plt.hist(total_IW2, range_used, histtype="bar", density=True, align='left', edgecolor='k')
locs, labels = plt.xticks(range_used)
locs, labels = plt.yticks(yrange)
plt.xlabel(xaxisa)
plt.ylabel(yaxis)
plt.title(ttlb)
plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()])

# total, both
fig, ax = plt.subplots()
n, bins, patches = plt.hist((total_IW, total_IW2), range_used, histtype="bar", label=("IW in terms of Announced MSS", "IW in terms of Recorded MSS"), density=True, align='left')
locs, labels = plt.xticks(range_used)
locs, labels = plt.yticks(yrange)
plt.xlabel("Initial Window Size (Announced or Recorded MSS)")
plt.ylabel(yaxis)
plt.title(ttl + "Announced and Recorded MSS")
plt.legend()
plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()])




# diff tls
fig, ax = plt.subplots()
n, bins, patches = plt.hist((all_HTTP_IW, all_HTTP_IW2, all_HTTPS_IW, all_HTTPS_IW2),
range_used, histtype="bar", color=("b", "midnightblue", "r", "brown"),
label=("HTTP Announced MSS", "HTTP Recorded MSS", "HTTPS Announced MSS", "HTTPS Recorded MSS"), density=True, align='left')

locs, labels = plt.xticks(range_used)
plt.xlabel("Initial Window Size (MSS)")
plt.ylabel(yaxis)
plt.title(ttl + "Split by HTTP/HTTPS")
plt.legend()
plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()])

# diff ip
fig, ax = plt.subplots()
n, bins, patches = plt.hist((all_v4_IW, all_v4_IW2, all_v6_IW, all_v6_IW2),
range_used, histtype="bar", color=("b", "midnightblue", "r", "brown"),
label=("IPv4 Announced MSS", "IPv4 Recorded MSS", "IPv6 Announced MSS", "IPv6 Recorded MSS"), density=True, align='left')
locs, labels = plt.xticks(range_used)
plt.xlabel("Initial Window Size (MSS)")
plt.ylabel(yaxis)
plt.title(ttl + "Split by IPv4/IPv6")
plt.legend()
plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()])



# diff tls
fig, ax = plt.subplots()
n, bins, patches = plt.hist((all_HTTP_IW2, all_HTTPS_IW2), range_used,
histtype="bar", label=("HTTP", "HTTPS"), align='left')
locs, labels = plt.xticks(range_used)
plt.xlabel("Initial Window Size (MSS)")
plt.ylabel(yaxis)
plt.title(ttl + "Split by HTTP/HTTPS")
plt.legend()
# plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()])

# diff ip
fig, ax = plt.subplots()
n, bins, patches = plt.hist((all_v4_IW2, all_v6_IW2), range_used,
histtype="bar", label=("IPv4", "IPv6"), align='left')
locs, labels = plt.xticks(range_used)
plt.xlabel("Initial Window Size (MSS)")
plt.ylabel(yaxis)
plt.title(ttl + "Split by IPv4/IPv6")
plt.legend()
# plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()])


plt.show()


def draw_plot(lists, mss, lbl, xaxis, yaxis, ttl):
    fig, ax = plt.subplots()
    n, bins, patches = plt.hist(lists, range_used, histtype="bar", label=lbl, density=True, align='left', edgecolor='k')
    locs, labels = plt.xticks(range_used)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(ttl)
    plt.legend()


#
