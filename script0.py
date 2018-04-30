import testlib
import time

pcap_file = "late_april2.pcapng"

# set up the arguments properly
# -q dont print total number packets until the end, -l flush output buffer,
start_tshark_args = [("tshark", "-i", "2", "-a", "duration:36000", "-q", "-l", "-w", pcap_file)]


# new with moved variable SACK and IPv6
# read pcap_file, -T fields select the information to retieve
new_proc_tshark_args = ["tshark", "-r", pcap_file, "-T", "fields", "-E", "separator=,", "-E", "aggregator=/s",
"-e", "ip.addr", "-e", "ipv6.addr", "-e", "tcp.port", "-e", "tcp.len", "-e", "tcp.options.mss_val",
"-e", "tcp.analysis.ack_rtt", "-e", "tcp.flags.syn", "-e", "frame.time_relative",
"-e", "tcp.window_size", "-e", "tcp.seq", "-e", "tcp.ack", "-e", "tcp.flags.fin",
"-e", "ssl.change_cipher_spec", "-e", "tcp.options.sack_le", "-e", "tcp.options.sack_re"]
# change connectionclass!!!

# IPv4, IPv6, Ports, TCP len, MSS, RTT, SYN, time, rwin, seq, ack, fin, cipher, sack

# testlib.capture_pkts(start_tshark_args)
# print("capture_pkts done")
#
# time.sleep(5)
#
# testlib.measure_connections("top-1m.txt", use_browser=False)
# print("measure_connections done")
#
# time.sleep(60)

testlib.process_capt_pkts(new_proc_tshark_args)
print("proc_capt_pkts done")



#
