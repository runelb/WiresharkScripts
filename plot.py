import connectionclass
import matplotlib.pyplot as plt

# find packet loss, resets
# option for source/destination/both

# ways to find useful averages etc for many connections

## packet lengths
def plot_from_packets(paramY, read_source):
    connection_Y = []   # temporary lists for individual connections
    connection_X = []
    plots_in_window = 0
    fig, ax = plt.subplots()
    if paramY == "length":
        ylabel = "Length (Bytes)"
    elif paramY == "rtt":
        ylabel = "RTT (ms)"
    elif paramY == "window":
        ylabel = "Window Size (Bytes)"
    elif paramY == "seq":
        ylabel = "Sequence (Bytes)"
    elif paramY == "ack":
        ylabel = "Ack (Bytes)"
    elif paramY == "throughput":
        ylabel = "Throughput (bps of payload)"
    elif paramY == "btlBW":
        ylabel = "BtlBw (Mbps)"
    elif paramY == "RTprop":
        ylabel = "RTprop (ms)"
    elif paramY == "BDP":
        ylabel = "BDP (bits)"
    title = paramY
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Time (s)")
    for c in connectionclass.connections:
        if read_source:
            c_ip = c.source
            name = c.destination
        else:
            c_ip = c.destination
            name = c.source
        if c_ip == connectionclass.find_most_used_ip():
            if paramY == "length" or "rtt" or "window" or "seq" or "ack":
                for p in c.sent_packets:
                    try:
                        if paramY == "length":
                            if p.length and p.timestamp:
                                connection_Y.append(p.length)
                                connection_X.append(p.timestamp)
                        elif paramY == "rtt":
                            if p.rtt and p.timestamp:
                                connection_Y.append(p.rtt)
                                connection_X.append(p.timestamp)
                        elif paramY == "window":
                            if p.window and p.timestamp:
                                connection_Y.append(p.cumulative_window)
                                connection_X.append(p.connection_timestamp)
                        elif paramY == "seq":
                            if p.seq and p.timestamp:
                                connection_Y.append(p.seq)
                                connection_X.append(p.connection_timestamp)
                        elif paramY == "ack":
                            if p.seq and p.timestamp:
                                connection_Y.append(p.ack)
                                connection_X.append(p.timestamp)
                    except: continue
            try:
                if paramY == "throughput":
                    plt.plot(c.throughput_time, c.throughput, 'o-', label=name)
                elif paramY =="btlBW":
                    plt.plot(c.RTprop_time, c.est_btlBW, 'o-', label=name)
                elif paramY =="RTprop":
                    plt.plot(c.RTprop_time, c.est_RTprop, 'o-', label=name)
                elif paramY == "BDP":
                    plt.plot(c.BDP_time, c.Bandwidth_delay_product, 'o-', label=name)
            except: continue
            try:
                plt.plot(connection_X, connection_Y, 'o-', label=name)
            except: continue
            try:
                ax.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
            except: continue
            connection_Y = []         # clear lists
            connection_X = []
            plots_in_window += 1
            if plots_in_window > 9:
                plots_in_window = 0
                fig, ax = plt.subplots()
                plt.title(title)
                plt.ylabel(ylabel)
                plt.xlabel("Time (s)")



connectionclass.sort_packets()
# connectionclass.calculate_throughput()

# plot_from_packets("length", 0)
# plot_from_packets("rtt", 0)
# plot_from_packets("throughput", 0)
# plot_from_packets("window", 1)
plot_from_packets("seq", 0)
# plot_from_packets("ack", 1)

# plot_from_packets("throughput", 0)
# plot_from_packets("btlBW", 0)
# plot_from_packets("RTprop", 0)
# plot_from_packets("BDP", 0)


# write code to get all info for specific connection, instead of specific info for all connections!!!
# aaaaahhhh


plt.show()




#
